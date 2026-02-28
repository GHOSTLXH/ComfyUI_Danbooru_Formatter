
# ==============================================================================
# 节点 1: 基础格式化与严格校验 (原版功能)
# ==============================================================================
class DanbooruTagFormatter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "1girl, solo..."}),
                "strict_danbooru_check": ("BOOLEAN", {"default": False, "label_on": "Enable Error", "label_off": "Disable Error"}), 
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_text",)
    FUNCTION = "process_tags"
    CATEGORY = "utils/text"

    def process_tags(self, text, strict_danbooru_check):
        if not text or not text.strip():
            return ("",)

        # 校验：如果完全没有逗号，且包含空格，判定为自然语言句子
        if ',' not in text and ' ' in text.strip():
             # 这里如果不加限制，单个tag如"blue eyes"也会报错，这符合"严格检查"的定义
             if strict_danbooru_check:
                 raise ValueError(f"[Formatter Error] 检测到自然语言或格式错误（未检测到逗号）：\n'{text}'\n请使用逗号分隔 Tag。")

        raw_tags = text.split(',')
        cleaned_tags = []

        for tag in raw_tags:
            stripped_tag = tag.strip()
            if not stripped_tag:
                continue

            if strict_danbooru_check:
                if ' ' in stripped_tag:
                    # 排除 Lora <...> 和权重 (...) 语法
                    if not (stripped_tag.startswith('<') or stripped_tag.startswith('(')):
                         raise ValueError(f"[Formatter Error] Tag含有非法空格: '{stripped_tag}'。\n请使用下划线 '_' 或关闭严格检查模式。")
            
            cleaned_tags.append(stripped_tag)

        return (", ".join(cleaned_tags),)


# ==============================================================================
# 节点 2: 自动修正空格为下划线 (新增功能)
# ==============================================================================
class DanbooruTagSnakeCaseFixer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False, "placeholder": "1girl, blue eyes, solo..."}),
                # 依然保留一个开关，用于控制是否要拦截"纯自然语言"
                "reject_natural_language": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("fixed_text",)
    FUNCTION = "fix_tags"
    CATEGORY = "utils/text"

    def fix_tags(self, text, reject_natural_language):
        if not text or not text.strip():
            return ("",)

        # --- 步骤1: 宏观格式检测 (报错机制) ---
        # 逻辑：如果输入是一个很长的句子（含空格），且完全没有逗号，判定为自然语言，报错。
        # 例如输入 "A girl is standing in the rain"，我们不希望它变成 "A_girl_is_standing_in_the_rain"
        if reject_natural_language:
            if ',' not in text and ' ' in text.strip():
                # 为了避免误伤单个Tag（如只输入了一个 "blue eyes"），我们做一个简单长度判断
                # 如果单词数超过3个且无逗号，基本判定为句子
                word_count = len(text.strip().split())
                if word_count > 3:
                    raise ValueError(f"[Fixer Error] 检测到疑似自然语言句子（单词数>3且无逗号）：\n'{text}'\n本节点仅处理以逗号分隔的 Tag 列表。")

        # --- 步骤2: 处理与自动修正 ---
        raw_tags = text.split(',')
        processed_tags = []

        for tag in raw_tags:
            # 去除首尾（分隔符周边的）空格
            clean_tag = tag.strip()
            
            if not clean_tag:
                continue

            # 自动修正逻辑：
            # 检测 Tag 内部是否有空格。如果有，替换为下划线。
            # 如果已经是下划线或无空格，replace 不会产生变化。
            
            # 保护机制：跳过 Lora 语法 <lora:name:1.0> 或 复杂权重 (tag:1.1)
            # 如果你希望连括号里的内容也强制加下划线，可以去掉这个判断
            if clean_tag.startswith('<') and clean_tag.endswith('>'):
                # Lora 保持原样
                final_tag = clean_tag
            else:
                # 执行替换: "blue eyes" -> "blue_eyes"
                final_tag = clean_tag.replace(' ', '_')

            processed_tags.append(final_tag)

        # --- 步骤3: 格式化输出 ---
        # 使用 ", " 重新连接
        return (", ".join(processed_tags),)


# ==============================================================================
# 节点映射
# ==============================================================================
NODE_CLASS_MAPPINGS = {
    "DanbooruTagFormatter": DanbooruTagFormatter,
    "DanbooruTagSnakeCaseFixer": DanbooruTagSnakeCaseFixer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DanbooruTagFormatter": "Danbooru Tag Formatter (Strict)",
    "DanbooruTagSnakeCaseFixer": "Danbooru Tag Auto-Fixer (Spaces to _)"
}