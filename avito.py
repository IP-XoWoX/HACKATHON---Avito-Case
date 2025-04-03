import sys

from PIL import Image
from PIL import ImageEnhance
from rembg import remove
import csv

def rgb_to_color_name(requested_color):
    color_names = {
        (243, 235, 196): 'бежевый',
        (159, 139, 116): 'бежевый',
        (196, 190, 159): 'бежевый',
        (183, 168, 144): 'бежевый',
        (255, 239, 216): 'бежевый',
        (235, 184, 126): 'бежевый',
        (219, 201, 178): 'бежевый',
        (255, 255, 255): 'белый',
        (229, 223, 226): 'белый',
        (210, 210, 210): 'белый',
        (109, 243, 230): 'бирюзовый',
        (0, 191, 255): 'голубой',
        (169, 176, 245): 'голубой', # uslss
        (180, 219, 249): 'голубой',
        (157, 165, 206): 'голубой',
        (0, 0, 255): 'синий',
        (115, 59, 87): 'бордовый',
        (87, 24, 32): 'бордовый',
        (110, 38, 50): 'бордовый',
        # (255, 255, 0): 'жёлтый', #uslss
        (230, 222, 105): 'жёлтый',
        (176, 163, 73): 'жёлтый',
        # (0, 255, 0): 'зелёный', # uslss
        (78, 175, 117): 'зелёный',
        # (94, 186, 131): 'зелёный', # uslss
        (212, 181, 55): 'золотой',
        (150, 75, 0): 'коричневый',
        (94, 77, 55): 'коричневый',
        (108, 99, 64): 'коричневый',
        (121, 96, 90): 'коричневый',
        (135, 114, 95): 'коричневый',
        (128, 109, 87): 'коричневый',
        (102, 58, 29): 'коричневый',
        (75, 29, 17): 'коричневый',
        (210, 167, 102): 'коричневый',
        # (255, 0, 0): 'красный', #uslss
        (148, 0, 0): 'красный',
        (255, 100, 0): 'оранжевый',
        # (199, 94, 133): 'розовый', # uslss
        (174, 88, 125): 'розовый',
        (238, 136, 193): 'розовый',
        (201, 152, 206): 'розовый',
        (183, 152, 126): 'розовый',
        (210, 44, 111): 'розовый',
        (170, 169, 176): 'серебристый',
        (121, 119, 112): 'серый',
        (106, 17, 173): 'фиолетовый',
        (74, 23, 108): 'фиолетовый',
        # (0, 0, 0): 'чёрный', #uslss
        (39, 42, 47): 'чёрный',
        (60, 58, 56): 'чёрный',
        (37, 14, 12): 'чёрный'
    }

    closest_color = (16581375, 'xd')
    for color in color_names:
        distance = (color[0] - requested_color[0]) ** 2 + (color[1] - requested_color[1]) ** 2 + (
                    color[2] - requested_color[2]) ** 2
        if distance < closest_color[0]:
            closest_color = (distance, color_names[color])

    return closest_color[1]

RARE_PIXEL_CUTOFF = 0.02
DEBUG_MODE = False
PRECISION = 19


def get_colors(img):
    total_pixels = 0
    colors = {}

    w, h = img.size

    for x in range(w):
        for y in range(h):
            r, g, b, a = img.getpixel((x, y))
            if a <= 250:
                continue

            total_pixels += 1

            for color in colors:
                if abs(r - color[0]) < PRECISION and abs(g - color[1]) < PRECISION and abs(b - color[2]) < PRECISION:
                    colors[color] += 1
                    break
            else:
                colors[(r, g, b)] = 1

    xdxdxd = dict(sorted(colors.items(), key=lambda x: x[1], reverse=True)[:8])
    for i in xdxdxd:
        print(i, xdxdxd[i], rgb_to_color_name(i))

    named_colors = {
        'бежевый': 0,
        'белый': 0,
        'бирюзовый': 0,
        'голубой': 0,
        'синий': 0,
        'бордовый': 0,
        'жёлтый': 0,
        'зелёный': 0,
        'золотой': 0,
        'коричневый': 0,
        'красный': 0,
        'оранжевый': 0,
        'розовый': 0,
        'серебристый': 0,
        'серый': 0,
        'фиолетовый': 0,
        'чёрный': 0
    }

    for clr in colors:
        if colors[clr] >= total_pixels * RARE_PIXEL_CUTOFF:
            named_colors[rgb_to_color_name(clr)] += colors[clr]

    return dict(sorted(named_colors.items(), key=lambda x: x[1], reverse=True)), total_pixels


def remove_background(img):
    return remove(img)


def get_processed_image(img):
    width, height = img.size

    # Уменьшение разрешения до 180p
    res_scaler = min(180 / height, 1)
    new_size = (int(width * res_scaler), int(height * res_scaler))
    im_resized = img.resize(new_size)

    # Удаление фона
    im_no_bg = remove_background(im_resized)

    # Увеличение насыщенности для более явного цвета
    im_sat = ImageEnhance.Color(im_no_bg).enhance(1.25)

    return im_sat


def get_color_judgement(colors_dict):
    total_selected_pixels = sum(colors_dict.values())

    if total_selected_pixels == 0:
        return ('разноцветный', 0), ('разноцветный', 0), ('разноцветный', 0)

    color_groups = {
        'blues': ('бирюзовый', 'голубой', 'синий'),
        'reds': ('красный', 'оранжевый', 'розовый', 'фиолетовый', 'бордовый'),
        'greys': ('белый', 'серебристый', 'серый'),
        'browns': ('бежевый', 'коричневый', 'золотой', 'жёлтый'), #new
        'blacks': ('чёрный'),
        'greens': ('зелёный')
    }
    color_group_pixels = {
        'blues': 0,
        'reds': 0,
        'greys': 0,
        'browns': 0,
        'yellows': 0,
        'blacks': 0,
        'greens': 0
    }
    colors_freq_dict = {}

    for color in colors_dict:
        colors_freq_dict[color] = colors_dict[color] / total_selected_pixels

        for group in color_groups:
            if color in color_groups[group]:
                color_group_pixels[group] += colors_dict[color]
                break

    if DEBUG_MODE:
        """ ДЕБАГ: Вывод значений цветовых групп """
        print("\n\tГруппы цветов по пикселям:")
        for i in color_group_pixels:
            print(i, color_group_pixels[i], sep='\t')

    """ Определение вероятности разноцветности """
    first_max_group = 0
    second_max_group = 0

    for group in color_group_pixels:
        if color_group_pixels[group] > first_max_group:
            first_max_group, second_max_group = color_group_pixels[group], first_max_group
        elif color_group_pixels[group] > second_max_group:
            second_max_group = color_group_pixels[group]

    colors_freq_dict["разноцветный"] = second_max_group / first_max_group

    colors_freq_dict = dict(sorted(colors_freq_dict.items(), key=lambda item: item[1], reverse=True))
    sorted_freq_colors = [*colors_freq_dict]

    if DEBUG_MODE:
        print("\n\tОсновные цвета по частоте:")
        for i in colors_freq_dict:
            print(i, colors_freq_dict[i])


    """ Увеличение веса наиболее вероятного предположения """
    scaler = 0.05
    s = 0

    for i, color in enumerate(sorted_freq_colors[1:]):
        colors_freq_dict[color] *= 1 - scaler*i
        s += colors_freq_dict[color] * (1 - scaler*i)

    colors_freq_dict[sorted_freq_colors[0]] = 1-s

    return colors_freq_dict


def identify_goods_color(img):
    im_processed = get_processed_image(img)
    named_colors, total_visible_pixels = get_colors(im_processed)

    if DEBUG_MODE:
        print("\n\tОсновные цвета по пикселям:")
        for i in named_colors:
            print(i, named_colors[i])

    guess_dict = get_color_judgement(named_colors)
    final_guess = [*guess_dict][0]

    print("\n\tИтоговая оценка цвета:")
    print(guess_dict, final_guess)

    # im_processed.show()

    return guess_dict, final_guess

""" Поиск изображения в датасете по имени (.jpg / .png) """
def find_image(folder_path, image_filename):
    full_path_no_ext = folder_path + '/' + image_filename
    try:
        print("\tTrying", full_path_no_ext + '.jpg')
        image = Image.open(full_path_no_ext + '.jpg')
    except:
        print("\tNot found", full_path_no_ext + '.jpg')
        try:
            print("\tTrying", full_path_no_ext + '.png')
            image = Image.open(full_path_no_ext + '.png')
        except:
            print("\tImage", image_filename, "not found")
            exit(-1)
        else:
            print("\tImage", full_path_no_ext + '.png', "successfully opened")
    else:
        print("\tImage", full_path_no_ext + '.jpg', "successfully opened")
    print()

    return image


def get_submission_eval(test_data_image_folder_path, test_data_csv_path, submission_path):
    with open(test_data_csv_path, encoding="utf8") as csv_input, open(submission_path+'/submission.csv', 'w', encoding="utf8") as csv_output:
        test_data_metadata = csv.DictReader(csv_input)
        writer = csv.writer(csv_output)

        writer.writerow(["id", "category", "predict_proba", "predict_color"])

        for input_row in test_data_metadata:
            image = find_image(test_data_image_folder_path, input_row['id'])
            color_eval, final_guess = identify_goods_color(image)

            output = [input_row["id"],input_row["category"], str(color_eval), final_guess]

            print(output)
            writer.writerow(output)


def main():
    get_submission_eval(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()

