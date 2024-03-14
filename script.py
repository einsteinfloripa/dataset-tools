from pathlib import Path


p = Path(['something'])
# def process_file(input_file, output_file):
#     with open(input_file, 'r') as f:
#         lines = f.readlines()

#     updated_lines = []

#     for line in lines:
#         values = line.split()
#         first_number = int(values[0])
#         updated_values = [str(min(float(val), 1.0)) for val in values[1:]]
#         updated_line = f"{first_number-2} {' '.join(updated_values)}\n"
#         updated_lines.append(updated_line)

#     with open(output_file, 'w') as f:
#         f.writelines(updated_lines)


# files = Path('').glob('PS_second_stage\\labels\\train\\*.txt')
# for filepath in files:
#     process_file(filepath, f'data\\{filepath.name}')




# for filepath in files:

#     # print(filepath)

#     cont = 0
#     with open(filepath, 'r+', encoding='utf8') as f:  
#         print(filepath)  
        
#         data = f.readlines()
#         f.truncate(0)
#         f.seek(0)

#         exit_text = ''
#         for line in data:
#             if int(line[0] + line[1]) > 5:
#                 print(filepath)
#                 break
#             else:
#                 # print(filepath)
#                 # cont += 1
#                 n = int(line[0] + line[1]) + 2
#                 exit_text += f'{str(n)}' + line[1:]

#         exit_text = exit_text.strip('\n')
#         f.write(exit_text)

# # print(cont)




# cpf_column
# question_line
# selected_ball
# unselected_ball
# question_number
# question_column
