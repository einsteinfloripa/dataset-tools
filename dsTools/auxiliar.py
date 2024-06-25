import inspect
import math
import cv2
from pathlib import Path

###### PATH RELATED FUNCTIONS ######

def mkdir_if_success(func):
    '''
    Decorator
    Cria um diretório para salvar os arquivos de saída da função.
    * Se o diretório já existir, levanta uma exceção.
    * Se a função falhar, deleta o diretório criado.
    '''
    par = inspect.signature(func).parameters.get("output_dir")
    def wrapper(*args, **kwargs):
        append = kwargs.get('append_to_dir', False)
        try: 
            path = Path(kwargs["output_dir"])
        except KeyError:
            path = Path(par.default)
        
        if path.exists() and not append:
            raise FileExistsError(f"{path} already exists.")
        path.mkdir(parents=True, exist_ok=True)
        
        try:
            func(*args, **kwargs)
        except Exception as e:
            if not append:
                path.rmdir()
            raise e
    return wrapper

class PathParsers:
    @staticmethod
    def get_img_label_pairs(path: str, ignore_single=False) -> list[tuple[str, str]]:
        '''
        Recebe um caminho para um diretório contendo imagens e labels.
        Retorna uma lista de tuplas contendo o caminho para a imagem e o caminho para o label.
        
        * Procura por arquivos .jpg e .png para as imagens.
        * Procura por arquivos .txt para os labels.
        * Se ignore_single=False, levanta um erro ao encontrar IMAGENS sem LABEL.
        '''
        path = Path(path)
        if not path.is_dir():
            return [PathParsers.get_img_label_pair(path)]
        img_files = list(path.glob("*.jpg")) + list(path.glob("*.png"))
        label_files = list(path.glob("*.txt"))
        
        if len(img_files) != len(label_files):
            raise ValueError(f"Number of images and labels do not match in {path}")

        labels = []
        for l in label_files:
            labels.append(l.stem)
        found = []
        for img in img_files:
            if img.stem in labels:
                found.append((str(img), f"{str(img.parent)}/{str(img.stem)}.txt"))
                continue
            if not ignore_single:    
                raise ValueError(f"Image {img} does not have a label file in {path}")
            
        return found

    @staticmethod
    def get_img_label_pair(namepath: str) -> tuple[str, str]:
        '''
        Recebe o caminho para um arquivo de imagem ou label.
        Retorna uma tupla contendo o caminho para a imagem e o caminho para o label.
        '''
        namepath = Path(namepath)
        path = namepath.parent
        name = namepath.name
        image = None
        for ext in ['.jpg', '.png']:
            img = path / (name + ext)
            if img.exists():
                image = img
                break
        if image is None:
            raise FileNotFoundError(f"Image not found for {namepath}")
        label = path / (name + '.txt')
        if not label.exists():
            raise FileNotFoundError(f"Label not found for {namepath}")
        return (str(image), str(label))

    @staticmethod
    def get_labels(path: str) -> list[str]:
        '''
        Recebe um caminho para um diretório contendo labels.
        Retorna uma lista contendo o caminho para cada label.
        '''
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Path {path} does not exist")
        if path.is_file():
            return [str(path)]
        label_files = list(path.glob("*.txt"))
        return [str(path) for path in label_files]

    @staticmethod
    def get_images(path: str) -> list[str]:
        '''
        Recebe um caminho para um diretório contendo imagens.
        Retorna uma lista contendo o caminho para cada imagem.
        '''
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Path {path} does not exist")
        if path.is_file():
            return [str(path)]
        img_files = list(path.glob("*.jpg")) + list(path.glob("*.png"))
        return [str(path) for path in img_files]

###### IMAGE PROCESSING FUNCTIONS ######

class Miscellaneous:
    '''Miscellaneous image processing functions'''

    @staticmethod
    def rotate_point(point, angle, origin):
        angle = math.radians(angle)
        w, h = origin
        x1, y1, = point
        # Transforma as coordenadas para o sistema cartesiano
        y1 = h - y1
        x1 -= w
        # Calcula a posiçao dos pontos após a rotação
        x1_ = x1 * math.cos(angle) - y1 * math.sin(angle)
        y1_ = x1 * math.sin(angle) + y1 * math.cos(angle)
        # Transforma as coordenadas para o sistema da imagem
        y1_ = h - y1_
        x1_ += w
        # Atualiza os valores'
        return (x1_, y1_)

    @staticmethod
    def ef_get_tilt(img, draw=False):
        '''Recebe uma prova einsteinfloripa e retorna o ângulo de inclinação da prova.'''
        # Cria uma cópia a parte superior da imagem
        img_ = img[0:int(img.shape[0]*0.15), 0:img.shape[1]].copy()
        # Aplica um blur para suavizar a imagem
        img_ = cv2.GaussianBlur(img_, (5, 5), 0)
        # Filtra a imagem para remover o ruído
        img_ = cv2.bilateralFilter(img_, 9, 75, 75)

        # Converte a imagem para tons de cinza
        # img_ = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
        
        # Aplica um filtro para detecçao de bordas
        edges = cv2.Canny(img_, 50, 200)
        # Detecta os contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Identifica os quadrados
        squares = []
        for cnt in contours:
            # Aproxima o contorno irregular por um polígono
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # Checa se a aproximaçao tem 4 lados e é convexo
            if len(approx) == 4 and cv2.isContourConvex(approx):
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                if 0.9 <= aspect_ratio <= 1.1:  # Aspect ratio perto de 1
                    squares.append(approx)
        
        # Encontra o centro de cada quadrado
        centers = []
        for square in squares:
            M = cv2.moments(square)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centers.append((cX, cY))
        centers.sort(key=lambda x: x[0])

        if draw:
            for square in squares:
                cv2.drawContours(img_, [square], -1, (0, 255, 0), 3)
            for center in centers:
                cv2.circle(img_, (cX, cY), 5, (255, 0, 0), -1) 
            cv2.imwrite("output.jpg", img_)

        # Calcula a inclinação da prova
        tilt = 0
        if len(squares) == 2:
            tilt = - math.degrees(math.atan( # menos porque o eixo y é invertido
                (centers[1][1] - centers[0][1]) / (centers[1][0] - centers[0][0])
            ))
            return tilt
        else:
            print("Could not find only two squares in the image.")
            return
