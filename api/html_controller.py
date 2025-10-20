from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 导入prompt_html.py中的提示词
from prompt_html import prompt_list, get_fix_prompt, get_modelfix_prompt

# 导入日志工具
from utils.logger_utils import logger, log_api_call

router = APIRouter()


# HTML修复接口
# 请求参数：html_content + template_content(可选)
# 请求方式：POST
# 返回参数：fixed_html
# 使用 prompt_list["prompt_fix"] 获取系统提示词， html_content 和 template_content 作为消息 请求大模型 获取结果
@router.post("/html_fix")
@log_api_call("/html_fix", "POST")
async def html_fix(request: dict = Body(...)):
    try:
        # 记录业务逻辑开始
        logger.business_logic("html_fix", "开始处理HTML修复请求")
        
        # 提取请求参数
        html_content = request.get("html_content", "")
        template_content = request.get("template_content", "")
        
        # 记录参数信息
        logger.parameters(
            (f"html_content长度: {len(html_content)}", "Integer"),
            (f"template_content长度: {len(template_content)}", "Integer")
        )
        
        if not html_content:
            logger.error("html_fix", "html_content 参数为空")
            raise HTTPException(status_code=400, detail="html_content 参数不能为空")
        
        # 获取系统提示词
        logger.business_logic("html_fix", "获取系统提示词")
        system_prompt = prompt_list["prompt_fix"]
        
        # 构建用户消息
        user_message = f"需要修复的HTML代码：\n```html\n{html_content}\n```"
        
        # 如果提供了模板内容，添加到用户消息中
        if template_content:
            user_message += f"\n\n参考模板/案例页面：\n```html\n{template_content}\n```"
        
        # 调用OpenAI API
        logger.business_logic("html_fix", "初始化OpenAI客户端")
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        # 记录模型推理开始
        model_name = os.getenv("LITE_TEXT_API_MODEL")
        logger.model_inference(model_name, input_tokens=len(user_message) + len(system_prompt))
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=12000
        )
        response_time = time.time() - start_time
        
        fixed_html = response.choices[0].message.content
        
        # 记录模型推理结果
        logger.model_inference(
            model_name, 
            input_tokens=len(user_message) + len(system_prompt),
            output_tokens=len(fixed_html) if fixed_html else 0,
            response_time=response_time
        )
        
        # 记录修复结果信息
        logger.info(f"HTML修复完成 - 结果长度: {len(fixed_html) if fixed_html else 0}")
        logger.debug(f"修复结果预览: {fixed_html[:200] if fixed_html else 'None'}...")
        
        # 记录成功完成
        logger.business_logic("html_fix", "HTML修复请求处理完成")
        
        return {
            "success": True,
            "fixed_html": fixed_html,
            "message": "HTML修复完成"
        }
        
    except Exception as e:
        # 记录错误信息
        logger.error(f"html_fix 处理失败: {str(e)}")
        logger.api_error("/html_fix", "POST", str(e), type(e).__name__)
        raise HTTPException(status_code=500, detail=f"HTML修复失败: {str(e)}")


# HTML模板修复接口
# 请求参数：html_content + template_content + fix_mode
# 请求方式：POST
# 返回参数：fixed_html
# 使用 get_modelfix_prompt() 获取系统提示词，严格按照模板格式进行修复
@router.post("/html_template_fix")
@log_api_call("/html_template_fix", "POST")
async def html_template_fix(request: dict = Body(...)):
    try:
        # 记录业务逻辑开始
        logger.business_logic("html_template_fix", "开始处理HTML模板修复请求")
        
        # 提取请求参数
        html_content = request.get("html_content", "")
        template_content = request.get("template_content", "")
        fix_mode = request.get("fix_mode", "strict")  # strict: 严格模式, flexible: 灵活模式
        
        # 记录参数信息
        logger.parameters(
            (f"html_content长度: {len(html_content)}", "Integer"),
            (f"template_content长度: {len(template_content)}", "Integer"),
            (f"fix_mode: {fix_mode}", "String")
        )
        
        if not html_content:
            logger.error("html_template_fix", "html_content 参数为空")
            raise HTTPException(status_code=400, detail="html_content 参数不能为空")
        
        if not template_content:
            logger.error("html_template_fix", "template_content 参数为空")
            raise HTTPException(status_code=400, detail="template_content 参数不能为空")
        
        # 构建对话文本，包含模板内容
        conversation_text = f"""
## 📋 用户提供的模板内容：
```html
{template_content}
```

## 🔧 需要修复的HTML代码：
```html
{html_content}
```

## 🎯 修复要求：
- 修复模式：{fix_mode}
- 严格按照上述模板格式进行修复
- 确保修复后的HTML结构与模板100%一致
- 保持原始内容完整性，仅调整结构以匹配模板
"""
        
        # 获取系统提示词
        logger.business_logic("html_template_fix", "获取模板修复提示词")
        system_prompt = get_modelfix_prompt(conversation_text)
        
        # 调用OpenAI API
        logger.business_logic("html_template_fix", "初始化OpenAI客户端")
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        
        # 记录模型推理开始
        model_name = os.getenv("LITE_TEXT_API_MODEL", "gpt-4o")
        logger.model_inference(model_name, input_tokens=len(conversation_text) + len(system_prompt))
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请严格按照提供的模板格式修复HTML代码"}
            ],
            temperature=0.1,  # 使用更低的温度确保严格按照模板执行
            max_tokens=12000
        )
        response_time = time.time() - start_time
        
        fixed_html = response.choices[0].message.content
        
        # 记录模型推理结果
        logger.model_inference(
            model_name, 
            input_tokens=len(conversation_text) + len(system_prompt),
            output_tokens=len(fixed_html) if fixed_html else 0,
            response_time=response_time
        )
        
        # 记录修复结果信息
        logger.info(f"HTML模板修复完成 - 结果长度: {len(fixed_html) if fixed_html else 0}")
        logger.debug(f"修复结果预览: {fixed_html[:200] if fixed_html else 'None'}...")
        
        # 记录成功完成
        logger.business_logic("html_template_fix", "HTML模板修复请求处理完成")
        
        return {
            "success": True,
            "fixed_html": fixed_html,
            "fix_mode": fix_mode,
            "message": "HTML模板修复完成"
        }
        
    except Exception as e:
        # 记录错误信息
        logger.error(f"html_template_fix 处理失败: {str(e)}")
        logger.api_error("/html_template_fix", "POST", str(e), type(e).__name__)
        raise HTTPException(status_code=500, detail=f"HTML模板修复失败: {str(e)}")

