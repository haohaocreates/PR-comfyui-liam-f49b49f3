import sys
import os
from PIL import Image, ImageOps
# import folder_paths
import torch
import numpy as np
import requests
from io import BytesIO


path = os.path.dirname(os.path.realpath(__file__))

def open_image_from_url(url):
    response = requests.get(url)
    image_data = BytesIO(response.content)
    image = Image.open(image_data)
    return image

def open_image_from_input(file_name):
    image_path = path+"/../../input/"+file_name
    #folder_paths.get_annotated_filepath(file_name)
    image = Image.open(image_path)
    return image

def back_image(i):
    i = ImageOps.exif_transpose(i)
    image = i.convert("RGB")
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    if 'A' in i.getbands():
        mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
        mask = 1. - torch.from_numpy(mask)
    else:
        mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
    # print(f"2 image type: {type(image)}")
    return (image, mask.unsqueeze(0))


# 将RGB图像转换为灰度图像
def convert_to_gray_and_return_tensor_pil(image_tensor):
    # 将torch.Tensor转换为numpy数组
    image = image_tensor.numpy().squeeze()
    # 将numpy数组转换为PIL图像
    image = Image.fromarray((image * 255).astype(np.uint8))
    # 将RGB图像转换为灰度图像
    image = image.convert("L")
    # 将灰度图像复制到3个通道，使其看起来像RGB图像
    image = Image.merge("RGB", (image, image, image))
    # 将PIL图像转换回numpy数组
    image = np.array(image).astype(np.float32) / 255.0
    # 将numpy数组转换回torch.Tensor
    image_tensor = torch.from_numpy(image)[None,]
    return image_tensor

# 写入 txt 文件
def write_txt(file_path,data):
    # print(data)
    with open(file_path, 'w') as f:
        # 写入文件
        f.write(data)
        # print('写入成功:',file_path)
        return True
    

# 将RGB图像转换为灰度图像
def fill_img_color(image_tensor,fill_color=(0, 0, 0, 255), fill_size=(1020, 1020)):
    # 将torch.Tensor转换为numpy数组
    image = image_tensor.numpy().squeeze()
    # 将numpy数组转换为PIL图像
    image = Image.fromarray((image * 255).astype(np.uint8))
    # 在给定的尺寸上，将图片粘贴到一个带有填充颜色的背景上
    image = img_fill_by_img(image, fill_color, fill_size)
    # 将PIL图像转换回numpy数组
    image = np.array(image).astype(np.float32) / 255.0
    # 将numpy数组转换回torch.Tensor
    image_tensor = torch.from_numpy(image)[None,]
    return image_tensor


def img_fill_by_img(pil_img, fill_color=(0, 0, 0, 255), fill_size=(1020, 1020)):
    """
    在给定的尺寸上，将图片粘贴到一个带有填充颜色的背景上。
    Args:
        pil_img (PIL.Image.Image): 待粘贴的图片对象。
        fill_color (tuple): 背景填充颜色的 RGBA 值，默认为黑色 (0, 0, 0, 255)。
        fill_size (tuple): 背景图片的尺寸，默认为 (1020, 1020)。
    Returns:
        PIL.Image.Image: 处理后的图片对象。
    """
    # 创建填充颜色的背景图片
    empty_img = Image.new("RGBA", fill_size, fill_color)

    # 如果图片尺寸小于背景图片尺寸，则将其居中粘贴到背景图片上
    if pil_img.size[0] < fill_size[0] or pil_img.size[1] < fill_size[1]:
        # 计算粘贴位置使图像居中
        paste_position = ((fill_size[0] - pil_img.size[0]) // 2, (fill_size[1] - pil_img.size[1]) // 2)
        # 创建与背景图片大小相同的白色掩码
        # mask = Image.new("L", fill_size, 255)
        empty_img.paste(pil_img, paste_position)
        return empty_img
    else:
        return pil_img