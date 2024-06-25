import math
import numpy as np

from dataclasses import dataclass, field
from src.auxiliar import Miscellaneous as misc

@dataclass
class Bbox:

    x1: int
    y1: int
    x2: int
    y2: int
    img : np.ndarray = field(default=None)
    id: int = field(default=None)

    @classmethod
    def from_xywh(cls, x, y, w, h, img, id=None):
        return cls(
            int(x-w/2), int(y-h/2), int(x + w/2), int(y + h/2), img, id=id)
    
    def xywh(self):
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2), self.x2 - self.x1, self.y2 - self.y1
    
    def xyxy(self):
        return self.x1, self.y1, self.x2, self.y2
    
    def nxywh(self):
        iw = self.img.shape[1]
        ih = self.img.shape[0]
        return self.x1 / iw, self.y1 / ih, (self.x2 - self.x1) / iw, (self.y2 - self.y1) / ih

    def nxyxy(self):
        iw = self.img.shape[1]
        ih = self.img.shape[0]
        return self.x1 / iw, self.y1 / ih, self.x2 / iw, self.y2 / ih

    def tilt(self, angle):
        x, y, w, h = self.xywh()
        iw = self.img.shape[1]
        ih = self.img.shape[0]
        x, y = misc.rotate_point((x, y), angle, (iw/2, ih/2))
        angle = math.radians(angle)
        nw = w * math.cos(angle) + h * math.sin(angle)
        nh = h * math.cos(angle) + w * math.sin(angle)
        self.x1, self.y1, self.x2, self.y2 = int(x - nw/2), int(y - nh/2), int(x + nw/2), int(y + nh/2)
    
    def __lt__(self, other):
        # check if below entirely from the other
        vert_dist_from_other = self.y1 - other.y1
        self_height = self.y2 - self.y1
        # magic number 0.9 is the coeficient to allow an minor sobreposition of detections
        # and still be considered below 
        if abs(vert_dist_from_other) > self_height * 0.9:
            if vert_dist_from_other < 0:
                return True
            else:
                return False
            
        # check if right entirely from the other
        hor_dist_from_other = self.x1 - other.x1
        self_width = self.x2 - self.x1
        # same magic number as above
        if abs(hor_dist_from_other) > self_width * 0.9:
            if hor_dist_from_other < 0:
                return True
            else:
                return False

        if vert_dist_from_other >= hor_dist_from_other:
            return self.middle_point.y < other.middle_point.y
        else:
            return self.middle_point.x < other.middle_point.x
        