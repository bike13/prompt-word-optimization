from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 导入prompt.py中的提示词
from prompt import (
    get_prompt_evaluation,
    get_prompt_refinement
)

# 导入日志工具
from utils.logger_utils import logger, log_api_call

# 中文到英文维度的映射字典
DIMENSION_MAPPING = {
    "清晰度与特异性": "Clarity & Specificity",
    "上下文背景提供": "Context / Background Provided",
    "任务定义明确性": "Explicit Task Definition",
    "模型约束可行性": "Feasibility within Model Constraints",
    "避免歧义和矛盾": "Avoiding Ambiguity or Contradictions",
    "模型适配性": "Model Fit / Scenario Appropriateness",
    "输出格式要求": "Desired Output Format / Style",
    "角色设定": "Use of Role or Persona",
    "逐步推理引导": "Step-by-Step Reasoning Encouraged",
    "结构化指令": "Structured / Numbered Instructions",
    "简洁与详细平衡": "Brevity vs. Detail Balance",
    "迭代优化潜力": "Iteration / Refinement Potential",
    "示例演示": "Examples or Demonstrations",
    "不确定性处理": "Handling Uncertainty / Gaps",
    "幻觉最小化": "Hallucination Minimization",
    "知识边界意识": "Knowledge Boundary Awareness",
    "受众指定": "Audience Specification",
    "风格模仿": "Style Emulation or Imitation",
    "记忆锚定": "Memory Anchoring (Multi-Turn Systems)",
    "元认知触发": "Meta-Cognition Triggers",
    "发散与收敛思维管理": "Divergent vs. Convergent Thinking Management",
    "假设框架切换": "Hypothetical Frame Switching",
    "安全失败模式": "Safe Failure Mode",
    "渐进复杂度": "Progressive Complexity",
    "评估指标对齐": "Alignment with Evaluation Metrics",
    "校准请求": "Calibration Requests",
    "输出验证钩子": "Output Validation Hooks",
    "时间/努力估算": "Time/Effort Estimation Request",
    "伦理对齐或偏见缓解": "Ethical Alignment or Bias Mitigation",
    "限制披露": "Limitations Disclosure",
    "压缩/总结能力": "Compression / Summarization Ability",
    "跨学科桥接": "Cross-Disciplinary Bridging",
    "情感共鸣校准": "Emotional Resonance Calibration",
    "输出风险分类": "Output Risk Categorization",
    "自我修复循环": "Self-Repair Loops"
}

# 1. Clarity & Specificity  
# 2. Context / Background Provided  
# 3. Explicit Task Definition
# 4. Feasibility within Model Constraints
# 5. Avoiding Ambiguity or Contradictions 
# 6. Model Fit / Scenario Appropriateness
# 7. Desired Output Format / Style
# 8. Use of Role or Persona
# 9. Step-by-Step Reasoning Encouraged 
# 10. Structured / Numbered Instructions
# 11. Brevity vs. Detail Balance
# 12. Iteration / Refinement Potential
# 13. Examples or Demonstrations
# 14. Handling Uncertainty / Gaps
# 15. Hallucination Minimization
# 16. Knowledge Boundary Awareness
# 17. Audience Specification
# 18. Style Emulation or Imitation
# 19. Memory Anchoring (Multi-Turn Systems)
# 20. Meta-Cognition Triggers
# 21. Divergent vs. Convergent Thinking Management
# 22. Hypothetical Frame Switching
# 23. Safe Failure Mode
# 24. Progressive Complexity
# 25. Alignment with Evaluation Metrics
# 26. Calibration Requests 
# 27. Output Validation Hooks
# 28. Time/Effort Estimation Request
# 29. Ethical Alignment or Bias Mitigation
# 30. Limitations Disclosure
# 31. Compression / Summarization Ability
# 32. Cross-Disciplinary Bridging
# 33. Emotional Resonance Calibration
# 34. Output Risk Categorization
# 35. Self-Repair Loops

router = APIRouter()

# 测试端点
@router.get("/test")
@log_api_call("/test", "GET")
async def test_endpoint():
    logger.business_logic("test_endpoint", "处理测试请求")
    logger.info("测试端点被调用")
    return {
        "success": True,
        "message": "API is working",
        "test_data": "This is a test response"
    }

# 评估提示词
# 请求参数：prompt_content + dimensions
# 请求方式：POST
# 返回参数：prompt_evaluation
# 使用 get_prompt_evaluation(dimensions) 获取系统提示词， prompt_content 作为消息 请求大模型 获取结果
@router.post("/prompt_evaluation")
@log_api_call("/prompt_evaluation", "POST")
async def prompt_evaluation(request: dict = Body(...)):
    try:
        # 记录业务逻辑开始
        logger.business_logic("prompt_evaluation", "开始处理提示词评估请求")
        
        # 提取请求参数
        prompt_content = request.get("prompt_content", "")
        dimensions = request.get("dimensions", [])
        
        # 记录参数信息
        logger.parameters(
            (f"prompt_content长度: {len(prompt_content)}", "Integer"),
            (f"dimensions数量: {len(dimensions)}", "Integer"),
            (f"dimensions: {dimensions}", "Array")
        )
        
        if not prompt_content:
            logger.error("prompt_evaluation", "prompt_content 参数为空")
            raise HTTPException(status_code=400, detail="prompt_content 参数不能为空")
        
        if not dimensions:
            logger.error("prompt_evaluation", "dimensions 参数为空")
            raise HTTPException(status_code=400, detail="dimensions 参数不能为空")
        
        # 将英文维度数组转换为字符串格式，用于提示词模板
        dimensions_str = "\n".join([f"{i+1}. {dim}" for i, dim in enumerate(dimensions)])
        
        # 获取系统提示词
        logger.business_logic("prompt_evaluation", "获取系统提示词")
        system_prompt = get_prompt_evaluation(dimensions_str)
        
        # 调用OpenAI API
        logger.business_logic("prompt_evaluation", "初始化OpenAI客户端")
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        
        # 记录模型推理开始
        model_name = os.getenv("OPENAI_API_MODEL", "gpt-4o")
        logger.model_inference(model_name, input_tokens=len(prompt_content) + len(system_prompt))
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"```\n{prompt_content}\n```"}
            ],
            temperature=0.3,
            max_tokens=20000
        )
        response_time = time.time() - start_time
        
        evaluation_result = response.choices[0].message.content
        
        # 记录模型推理结果
        logger.model_inference(
            model_name, 
            input_tokens=len(prompt_content) + len(system_prompt),
            output_tokens=len(evaluation_result) if evaluation_result else 0,
            response_time=response_time
        )
        
        # 记录评估结果信息
        logger.info(f"评估完成 - 结果长度: {len(evaluation_result) if evaluation_result else 0}")
        logger.debug(f"评估结果预览: {evaluation_result[:200] if evaluation_result else 'None'}...")
        
        # 记录成功完成
        logger.business_logic("prompt_evaluation", "评估请求处理完成")
        
        return {
            "success": True,
            "evaluation_result": evaluation_result,
            "message": "评估完成"
        }
        
    except Exception as e:
        # 记录错误信息
        logger.error(f"prompt_evaluation 处理失败: {str(e)}")
        logger.api_error("/prompt_evaluation", "POST", str(e), type(e).__name__)
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")

# 优化提示词
# 请求参数：prompt_content + evaluation_result
# 请求方式：POST
# 返回参数：prompt_refinement
# 使用 get_prompt_refinement() 获取系统提示词， evaluation_result 和 prompt_content 作为消息 请求大模型 获取结果
@router.post("/prompt_refinement")
@log_api_call("/prompt_refinement", "POST")
async def prompt_refinement(request: dict = Body(...)):
    try:
        # 记录业务逻辑开始
        logger.business_logic("prompt_refinement", "开始处理提示词优化请求")
        
        # 提取请求参数
        prompt_content = request.get("prompt_content", "")
        evaluation_result = request.get("evaluation_result", "")
        
        # 记录参数信息
        logger.parameters(
            (f"prompt_content长度: {len(prompt_content)}", "Integer"),
            (f"evaluation_result长度: {len(evaluation_result)}", "Integer")
        )
        
        if not prompt_content:
            logger.error("prompt_refinement", "prompt_content 参数为空")
            raise HTTPException(status_code=400, detail="prompt_content 参数不能为空")
        
        if not evaluation_result:
            logger.error("prompt_refinement", "evaluation_result 参数为空")
            raise HTTPException(status_code=400, detail="evaluation_result 参数不能为空")
        
        # 获取系统提示词
        logger.business_logic("prompt_refinement", "获取系统提示词")
        system_prompt = get_prompt_refinement()
        
        # 构建用户消息，包含评估结果和原始提示词
        user_message = f"评估报告：\n{evaluation_result}\n\n原始提示词：\n```\n{prompt_content}\n```"
        
        # 调用OpenAI API
        logger.business_logic("prompt_refinement", "初始化OpenAI客户端")
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        
        # 记录模型推理开始
        model_name = os.getenv("OPENAI_API_MODEL", "gpt-4o")
        logger.model_inference(model_name, input_tokens=len(user_message) + len(system_prompt))
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=20000
        )
        response_time = time.time() - start_time
        
        refinement_result = response.choices[0].message.content
        
        # 记录模型推理结果
        logger.model_inference(
            model_name, 
            input_tokens=len(user_message) + len(system_prompt),
            output_tokens=len(refinement_result) if refinement_result else 0,
            response_time=response_time
        )
        
        # 记录优化结果信息
        logger.info(f"优化完成 - 结果长度: {len(refinement_result) if refinement_result else 0}")
        logger.debug(f"优化结果预览: {refinement_result[:200] if refinement_result else 'None'}...")
        
        # 记录成功完成
        logger.business_logic("prompt_refinement", "优化请求处理完成")
        
        return {
            "success": True,
            "refinement_result": refinement_result,
            "message": "优化完成"
        }
        
    except Exception as e:
        # 记录错误信息
        logger.error(f"prompt_refinement 处理失败: {str(e)}")
        logger.api_error("/prompt_refinement", "POST", str(e), type(e).__name__)
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")
