import os
from PIL import Image
from loguru import logger

def crop_image(image_path, mode='square'):
    """
    裁剪图片
    
    参数:
    - image_path: 图片路径
    - mode: 裁剪模式，可选值：'square'(正方形)、'vertical'(竖直)、'horizontal'(水平)
    
    返回:
    - 裁剪后的图片路径
    """
    try:
        logger.info(f"开始裁剪图片: {image_path}, 模式: {mode}")
        
        # 打开图片
        img = Image.open(image_path)
        width, height = img.size
        logger.info(f"原始图片尺寸: {width}x{height}")
        
        # 根据模式计算裁剪区域
        if mode == 'square':
            # 正方形裁剪，取中心区域
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            right = left + size
            bottom = top + size
        elif mode == 'vertical':
            # 竖直裁剪，宽高比3:4
            if width / height > 3/4:
                # 图片太宽，需要裁剪宽度
                new_width = int(height * 3/4)
                left = (width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = height
            else:
                # 图片太高，需要裁剪高度
                new_height = int(width * 4/3)
                left = 0
                top = (height - new_height) // 2
                right = width
                bottom = top + new_height
        elif mode == 'horizontal':
            # 水平裁剪，宽高比4:3
            if width / height < 4/3:
                # 图片太高，需要裁剪高度
                new_height = int(width * 3/4)
                left = 0
                top = (height - new_height) // 2
                right = width
                bottom = top + new_height
            else:
                # 图片太宽，需要裁剪宽度
                new_width = int(height * 4/3)
                left = (width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = height
        else:
            # 不支持的模式，返回原图
            logger.warning(f"不支持的裁剪模式: {mode}，返回原图")
            return image_path
        
        # 裁剪图片
        cropped_img = img.crop((left, top, right, bottom))
        logger.info(f"裁剪区域: ({left}, {top}, {right}, {bottom})")
        logger.info(f"裁剪后尺寸: {cropped_img.width}x{cropped_img.height}")
        
        # 检查图片模式，如果是RGBA，转换为RGB
        if cropped_img.mode == 'RGBA':
            logger.info("检测到RGBA模式图片，转换为RGB模式")
            cropped_img = cropped_img.convert('RGB')
        
        # 生成裁剪后的图片路径
        file_name, file_ext = os.path.splitext(image_path)
        cropped_image_path = f"{file_name}_crop{file_ext}"
        
        # 保存裁剪后的图片
        cropped_img.save(cropped_image_path)
        logger.info(f"裁剪后的图片已保存: {cropped_image_path}")
        
        return cropped_image_path
    except Exception as e:
        logger.error(f"图片裁剪失败: {str(e)}")
        # 如果裁剪失败，返回原图
        return image_path

def pad_image(image_path, mode='vertical'):
    """
    补全图片（而非裁剪）
    
    参数:
    - image_path: 图片路径
    - mode: 补全模式，可选值：'square'(正方形)、'vertical'(竖直)、'horizontal'(水平)
    
    返回:
    - 补全后的图片路径
    """
    try:
        logger.info(f"开始补全图片: {image_path}, 模式: {mode}")
        
        # 打开图片
        img = Image.open(image_path)
        width, height = img.size
        logger.info(f"原始图片尺寸: {width}x{height}")
        
        # 根据模式计算新的尺寸和位置
        if mode == 'square':
            # 正方形补全，取最大边长
            size = max(width, height)
            new_width = size
            new_height = size
        elif mode == 'vertical':
            # 竖直补全，宽高比3:4
            if width / height > 3/4:
                # 图片太宽，按宽度计算高度
                new_width = width
                new_height = int(width * 4/3)
            else:
                # 图片太高，按高度计算宽度
                new_width = int(height * 3/4)
                new_height = height
        elif mode == 'horizontal':
            # 水平补全，宽高比4:3
            if width / height < 4/3:
                # 图片太高，按高度计算宽度
                new_width = int(height * 4/3)
                new_height = height
            else:
                # 图片太宽，按宽度计算高度
                new_width = width
                new_height = int(width * 3/4)
        else:
            # 不支持的模式，返回原图
            logger.warning(f"不支持的补全模式: {mode}，返回原图")
            return image_path
        
        # 创建新图片（白色背景）
        padded_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))
        
        # 计算粘贴位置（居中）
        paste_x = (new_width - width) // 2
        paste_y = (new_height - height) // 2
        
        # 检查图片模式，如果是RGBA，需要特殊处理
        if img.mode == 'RGBA':
            logger.info("检测到RGBA模式图片，特殊处理透明通道")
            # 创建透明通道的掩码
            r, g, b, a = img.split()
            padded_img.paste(img, (paste_x, paste_y), mask=a)
        else:
            # 直接粘贴
            padded_img.paste(img, (paste_x, paste_y))
        
        logger.info(f"补全后尺寸: {padded_img.width}x{padded_img.height}")
        
        # 生成补全后的图片路径
        file_name, file_ext = os.path.splitext(image_path)
        padded_image_path = f"{file_name}_padded{file_ext}"
        
        # 保存补全后的图片
        padded_img.save(padded_image_path)
        logger.info(f"补全后的图片已保存: {padded_image_path}")
        
        return padded_image_path
    except Exception as e:
        logger.error(f"图片补全失败: {str(e)}")
        # 如果补全失败，返回原图
        return image_path

def main():
    """
    测试图片处理功能
    """
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python image_util.py <操作> <图片路径> [模式]")
        print("操作可选: crop, pad")
        print("模式可选: square, vertical, horizontal，默认为vertical")
        return
    
    operation = sys.argv[1]
    image_path = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'vertical'
    
    if not os.path.exists(image_path):
        print(f"错误: 图片 {image_path} 不存在")
        return
    
    if operation == 'crop':
        print(f"正在裁剪图片: {image_path}, 模式: {mode}")
        result_path = crop_image(image_path, mode)
    elif operation == 'pad':
        print(f"正在补全图片: {image_path}, 模式: {mode}")
        result_path = pad_image(image_path, mode)
    else:
        print(f"不支持的操作: {operation}")
        return
    
    print(f"处理完成，结果保存在: {result_path}")

if __name__ == "__main__":
    main()
