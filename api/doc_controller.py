"""
文档分析AI助手 - 核心实现
支持多种文档格式的解析、翻译和生成
"""

import os
import io
import base64
import mimetypes
import tempfile
import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import pdfplumber
from docx import Document
import fitz  # PyMuPDF
from PIL import Image
import requests

# 导入提示词配置
from prompt_doc import (
    DOCUMENT_TRANSLATION_PROMPT,
    IMAGE_TRANSLATION_PROMPT,
    DOCUMENT_SUMMARY_PROMPT
)

load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI路由器
router = APIRouter(tags=["文档处理"])


class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.openai_api_model = os.getenv("OPENAI_API_MODEL")
        self.lite_api_model = os.getenv("LITE_TEXT_API_MODEL")
        self.lite_vis_api_model = os.getenv("LITE_VIS_API_MODEL")
        
        # 初始化OpenAI客户端
        self.openai_client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )
        
        # 支持的文档格式
        self.supported_formats = {
            '.pdf': 'PDF',
            '.doc': 'Word',
            '.docx': 'Word',
            '.rtf': 'RTF',
            '.txt': 'Text',
            '.md': 'Markdown',
            '.html': 'HTML',
            '.htm': 'HTML'
        }
    
    def get_client(self, use_vision: bool = False) -> OpenAI:
        """获取OpenAI客户端"""
        if use_vision and self.openai_api_key:
            return OpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_api_base,
            )
        return self.openai_client


class DocumentParser(ABC):
    """文档解析器抽象基类"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    @abstractmethod
    def parse_content(self, file_path: str) -> Dict[str, Any]:
        """解析文档内容"""
        pass
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """提取文本内容"""
        pass
    
    @abstractmethod
    def extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """提取图片"""
        pass
    
    @abstractmethod
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取文档元数据"""
        pass
    
    @abstractmethod
    def get_structure(self, file_path: str) -> Dict[str, Any]:
        """获取文档结构"""
        pass


class PDFParser(DocumentParser):
    """PDF文档解析器"""
    
    def parse_content(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文档内容"""
        try:
            text_content = self.extract_text(file_path)
            images = self.extract_images(file_path)
            metadata = self.get_metadata(file_path)
            structure = self.get_structure(file_path)
            
            return {
                'text': text_content,
                'images': images,
                'metadata': metadata,
                'structure': structure,
                'type': 'PDF'
            }
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """提取PDF文本内容"""
        text_content = ""
        try:
            # 首先尝试PyPDF2，因为它更稳定
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"第{page_num+1}页提取失败: {e}")
                        continue
        except Exception as e:
            logger.error(f"PyPDF2提取失败: {e}")
            # 如果PyPDF2失败，尝试pdfplumber
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
            except Exception as e2:
                logger.error(f"pdfplumber也失败: {e2}")
        
        return text_content.strip()
    
    def extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """提取PDF中的图片"""
        images = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # 确保不是CMYK
                        img_data = pix.tobytes("png")
                        img_base64 = base64.b64encode(img_data).decode()
                        
                        images.append({
                            'page': page_num + 1,
                            'index': img_index,
                            'data': img_base64,
                            'format': 'png',
                            'size': (pix.width, pix.height)
                        })
                    pix = None
            
            doc.close()
        except Exception as e:
            logger.error(f"PDF图片提取失败: {e}")
        
        return images
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取PDF元数据"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': metadata.get('/Title', '') if metadata else '',
                    'author': metadata.get('/Author', '') if metadata else '',
                    'subject': metadata.get('/Subject', '') if metadata else '',
                    'creator': metadata.get('/Creator', '') if metadata else '',
                    'producer': metadata.get('/Producer', '') if metadata else '',
                    'creation_date': metadata.get('/CreationDate', '') if metadata else '',
                    'modification_date': metadata.get('/ModDate', '') if metadata else '',
                    'pages': len(pdf_reader.pages)
                }
        except Exception as e:
            logger.error(f"PDF元数据获取失败: {e}")
            return {}
    
    def get_structure(self, file_path: str) -> Dict[str, Any]:
        """获取PDF文档结构"""
        try:
            with pdfplumber.open(file_path) as pdf:
                structure = {
                    'pages': len(pdf.pages),
                    'tables': [],
                    'outline': []
                }
                
                # 提取表格信息
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    if tables:
                        structure['tables'].append({
                            'page': page_num + 1,
                            'count': len(tables)
                        })
                
                return structure
        except Exception as e:
            logger.error(f"PDF结构分析失败: {e}")
            return {'pages': 0, 'tables': [], 'outline': []}


class WordParser(DocumentParser):
    """Word文档解析器"""
    
    def parse_content(self, file_path: str) -> Dict[str, Any]:
        """解析Word文档内容"""
        try:
            text_content = self.extract_text(file_path)
            images = self.extract_images(file_path)
            metadata = self.get_metadata(file_path)
            structure = self.get_structure(file_path)
            
            return {
                'text': text_content,
                'images': images,
                'metadata': metadata,
                'structure': structure,
                'type': 'Word'
            }
        except Exception as e:
            logger.error(f"Word解析失败: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """提取Word文本内容"""
        try:
            doc = Document(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content.strip()
        except Exception as e:
            logger.error(f"Word文本提取失败: {e}")
            return ""
    
    def extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """提取Word中的图片"""
        images = []
        try:
            doc = Document(file_path)
            
            # 提取内嵌图片
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    image_data = rel.target_part.blob
                    img_base64 = base64.b64encode(image_data).decode()
                    
                    images.append({
                        'data': img_base64,
                        'format': rel.target_ref.split('.')[-1],
                        'type': 'embedded'
                    })
        except Exception as e:
            logger.error(f"Word图片提取失败: {e}")
        
        return images
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取Word元数据"""
        try:
            doc = Document(file_path)
            core_props = doc.core_properties
            
            return {
                'title': core_props.title or '',
                'author': core_props.author or '',
                'subject': core_props.subject or '',
                'keywords': core_props.keywords or '',
                'created': str(core_props.created) if core_props.created else '',
                'modified': str(core_props.modified) if core_props.modified else '',
                'pages': len(doc.paragraphs)
            }
        except Exception as e:
            logger.error(f"Word元数据获取失败: {e}")
            return {}
    
    def get_structure(self, file_path: str) -> Dict[str, Any]:
        """获取Word文档结构"""
        try:
            doc = Document(file_path)
            structure = {
                'paragraphs': len(doc.paragraphs),
                'tables': len(doc.tables),
                'sections': len(doc.sections),
                'headings': []
            }
            
            # 提取标题结构
            for paragraph in doc.paragraphs:
                if paragraph.style.name.startswith('Heading'):
                    structure['headings'].append({
                        'level': paragraph.style.name,
                        'text': paragraph.text
                    })
            
            return structure
        except Exception as e:
            logger.error(f"Word结构分析失败: {e}")
            return {}


class TextParser(DocumentParser):
    """纯文本解析器"""
    
    def parse_content(self, file_path: str) -> Dict[str, Any]:
        """解析文本文档内容"""
        try:
            text_content = self.extract_text(file_path)
            images = self.extract_images(file_path)  # 文本文件通常没有图片
            metadata = self.get_metadata(file_path)
            structure = self.get_structure(file_path)
            
            return {
                'text': text_content,
                'images': images,
                'metadata': metadata,
                'structure': structure,
                'type': 'Text'
            }
        except Exception as e:
            logger.error(f"文本解析失败: {e}")
            raise
    
    def extract_text(self, file_path: str) -> str:
        """提取文本内容"""
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用二进制模式读取
            with open(file_path, 'rb') as file:
                return file.read().decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            return ""
    
    def extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """文本文件通常没有图片"""
        return []
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取文本文件元数据"""
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'lines': len(self.extract_text(file_path).split('\n'))
            }
        except Exception as e:
            logger.error(f"文本元数据获取失败: {e}")
            return {}
    
    def get_structure(self, file_path: str) -> Dict[str, Any]:
        """获取文本文件结构"""
        try:
            text = self.extract_text(file_path)
            lines = text.split('\n')
            
            return {
                'lines': len(lines),
                'characters': len(text),
                'words': len(text.split()),
                'paragraphs': len([p for p in text.split('\n\n') if p.strip()])
            }
        except Exception as e:
            logger.error(f"文本结构分析失败: {e}")
            return {}


class ImageProcessor:
    """图片处理类"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def process_image(self, image_data: str, target_language: str = "中文") -> Dict[str, Any]:
        """处理图片：OCR识别和翻译"""
        try:
            # 使用视觉模型进行图片翻译
            client = self.config.get_client(use_vision=True)
            
            prompt = IMAGE_TRANSLATION_PROMPT.format(target_language=target_language)
            
            response = client.chat.completions.create(
                model=self.config.lite_vis_api_model or self.config.openai_api_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            
            result = response.choices[0].message.content
            
            return {
                'original_image': image_data,
                'translation_result': result,
                'processed': True
            }
            
        except Exception as e:
            logger.error(f"图片处理失败: {e}")
            return {
                'original_image': image_data,
                'translation_result': f"图片处理失败: {str(e)}",
                'processed': False
            }


class DocumentGenerator:
    """文档生成器类"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def generate_markdown(self, original_content: str, translated_content: str, 
                         images: List[Dict[str, Any]] = None) -> str:
        """生成Markdown格式的双语文档"""
        try:
            md_content = "# 双语文档\n\n"
            
            # 添加原文
            md_content += "## 原文\n\n"
            md_content += original_content + "\n\n"
            
            # 添加译文
            md_content += "## 译文\n\n"
            md_content += translated_content + "\n\n"
            
            # 添加图片信息
            if images:
                md_content += "## 图片内容\n\n"
                for i, img in enumerate(images):
                    if img.get('processed'):
                        md_content += f"### 图片 {i+1}\n\n"
                        md_content += f"**翻译结果：**\n{img.get('translation_result', '')}\n\n"
            
            return md_content
            
        except Exception as e:
            logger.error(f"Markdown生成失败: {e}")
            return f"文档生成失败: {str(e)}"
    
    def generate_html(self, original_content: str, translated_content: str,
                     images: List[Dict[str, Any]] = None) -> str:
        """生成HTML格式的双语文档"""
        try:
            html_content = """
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>双语文档</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .section { margin-bottom: 30px; }
                    .original { background-color: #f5f5f5; padding: 20px; border-left: 4px solid #007acc; }
                    .translated { background-color: #f0f8ff; padding: 20px; border-left: 4px solid #28a745; }
                    .image-section { margin: 20px 0; }
                    .image-result { background-color: #fff3cd; padding: 15px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>双语文档</h1>
                
                <div class="section">
                    <h2>原文</h2>
                    <div class="original">
                        <pre>{}</pre>
                    </div>
                </div>
                
                <div class="section">
                    <h2>译文</h2>
                    <div class="translated">
                        <pre>{}</pre>
                    </div>
                </div>
            """.format(original_content, translated_content)
            
            # 添加图片信息
            if images:
                html_content += '<div class="section"><h2>图片内容</h2>'
                for i, img in enumerate(images):
                    if img.get('processed'):
                        html_content += f'''
                        <div class="image-section">
                            <h3>图片 {i+1}</h3>
                            <div class="image-result">
                                <strong>翻译结果：</strong><br>
                                {img.get('translation_result', '')}
                            </div>
                        </div>
                        '''
                html_content += '</div>'
            
            html_content += """
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"HTML生成失败: {e}")
            return f"<html><body><h1>文档生成失败</h1><p>{str(e)}</p></body></html>"


class DocumentProcessor:
    """核心文档处理类"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.parsers = {
            'PDF': PDFParser(self.config),
            'Word': WordParser(self.config),
            'Text': TextParser(self.config)
        }
        self.image_processor = ImageProcessor(self.config)
        self.document_generator = DocumentGenerator(self.config)
    
    def detect_format(self, file_path: str) -> str:
        """检测文档格式"""
        file_ext = Path(file_path).suffix.lower()
        return self.config.supported_formats.get(file_ext, 'Unknown')
    
    def translate_text(self, text: str, target_language: str = "中文") -> str:
        """使用AI翻译文本"""
        try:
            client = self.config.get_client()
            prompt = DOCUMENT_TRANSLATION_PROMPT.format(
                content=text,
                target_language=target_language
            )
            
            response = client.chat.completions.create(
                model=self.config.openai_api_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"文本翻译失败: {e}")
            return f"翻译失败: {str(e)}"
    
    def process_document(self, file_path: str, target_language: str = "中文", 
                        output_format: str = "markdown") -> Dict[str, Any]:
        """处理文档的主要方法"""
        try:
            # 1. 检测文档格式
            doc_format = self.detect_format(file_path)
            if doc_format == 'Unknown':
                raise ValueError(f"不支持的文档格式: {Path(file_path).suffix}")
            
            logger.info(f"开始处理 {doc_format} 文档: {file_path}")
            
            # 2. 选择对应的解析器
            parser = self.parsers.get(doc_format)
            if not parser:
                raise ValueError(f"未找到 {doc_format} 解析器")
            
            # 3. 解析文档内容
            logger.info("开始解析文档内容...")
            parsed_content = parser.parse_content(file_path)
            logger.info(f"文档解析完成，文本长度: {len(parsed_content.get('text', ''))}")
            
            # 4. 翻译文本内容
            original_text = parsed_content['text']
            if not original_text.strip():
                logger.warning("文档中没有提取到文本内容")
                original_text = "文档中没有可提取的文本内容"
                translated_text = "No text content could be extracted from the document"
            else:
                logger.info("开始翻译文本内容...")
                translated_text = self.translate_text(original_text, target_language)
                logger.info("文本翻译完成")
            
            # 5. 处理图片 (暂时跳过，避免依赖问题)
            processed_images = []
            logger.info(f"跳过图片处理，图片数量: {len(parsed_content.get('images', []))}")
            
            # 6. 生成输出文档
            logger.info("开始生成输出文档...")
            if output_format.lower() == 'html':
                output_content = self.document_generator.generate_html(
                    original_text, translated_text, processed_images
                )
            else:
                output_content = self.document_generator.generate_markdown(
                    original_text, translated_text, processed_images
                )
            logger.info("输出文档生成完成")
            
            return {
                'success': True,
                'original_content': original_text,
                'translated_content': translated_text,
                'processed_images': processed_images,
                'output_content': output_content,
                'metadata': parsed_content.get('metadata', {}),
                'structure': parsed_content.get('structure', {}),
                'format': doc_format
            }
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def generate_summary(self, content: str) -> str:
        """生成文档摘要"""
        try:
            client = self.config.get_client()
            prompt = DOCUMENT_SUMMARY_PROMPT.format(content=content)
            
            response = client.chat.completions.create(
                model=self.config.openai_api_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return f"摘要生成失败: {str(e)}"


# 初始化文档处理器实例
processor = DocumentProcessor()


# ==================== API接口定义 ====================

@router.post("/upload")
async def upload_and_process_document(
    file: UploadFile = File(...),
    target_language: str = Form(default="中文"),
    output_format: str = Form(default="markdown")
):
    """
    上传并处理文档
    
    Args:
        file: 上传的文档文件
        target_language: 目标语言
        output_format: 输出格式 (markdown/html)
    
    Returns:
        处理结果
    """
    tmp_file_path = None
    try:
        logger.info(f"开始处理文档上传: {file.filename}")
        
        # 验证文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in processor.config.supported_formats:
            logger.error(f"不支持的文档格式: {file_ext}")
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文档格式: {file_ext}"
            )
        
        # 检查文件大小 (限制为50MB)
        file_size = 0
        content = b""
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            while True:
                chunk = await file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    raise HTTPException(
                        status_code=413,
                        detail="文件大小超过50MB限制"
                    )
                tmp_file.write(chunk)
                content += chunk
            
            tmp_file_path = tmp_file.name
        
        logger.info(f"文件上传完成: {file.filename}, 大小: {file_size} bytes")
        
        # 处理文档
        logger.info("开始文档处理...")
        result = processor.process_document(
            file_path=tmp_file_path,
            target_language=target_language,
            output_format=output_format
        )
        
        if result['success']:
            # 保存输出文件
            output_filename = f"{uuid.uuid4()}.{output_format}"
            output_path = f"outputs/{output_filename}"
            
            # 确保输出目录存在
            os.makedirs("outputs", exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['output_content'])
            
            logger.info(f"文档处理成功: {output_filename}")
            
            return JSONResponse({
                "success": True,
                "message": "文档处理成功",
                "data": {
                    "original_filename": file.filename,
                    "output_filename": output_filename,
                    "download_url": f"/api/doc/download/{output_filename}",
                    "format": result['format'],
                    "original_length": len(result['original_content']),
                    "translated_length": len(result['translated_content']),
                    "images_processed": len(result['processed_images']),
                    "metadata": result['metadata'],
                    "structure": result['structure']
                }
            })
        else:
            logger.error(f"文档处理失败: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=f"文档处理失败: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传处理异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    finally:
        # 清理临时文件
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
                logger.info(f"临时文件已清理: {tmp_file_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")


@router.get("/download/{filename}")
async def download_processed_document(filename: str):
    """
    下载处理后的文档
    
    Args:
        filename: 输出文件名
    
    Returns:
        文件下载响应
    """
    try:
        file_path = f"outputs/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-text")
async def translate_text(
    text: str = Form(...),
    target_language: str = Form(default="中文")
):
    """
    翻译文本内容
    
    Args:
        text: 要翻译的文本
        target_language: 目标语言
    
    Returns:
        翻译结果
    """
    try:
        translated_text = processor.translate_text(text, target_language)
        
        return JSONResponse({
            "success": True,
            "data": {
                "original_text": text,
                "translated_text": translated_text,
                "target_language": target_language
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary")
async def generate_summary(
    content: str = Form(...)
):
    """
    生成文档摘要
    
    Args:
        content: 文档内容
    
    Returns:
        摘要结果
    """
    try:
        summary = processor.generate_summary(content)
        
        return JSONResponse({
            "success": True,
            "data": {
                "original_content": content,
                "summary": summary
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-formats")
async def get_supported_formats():
    """
    获取支持的文档格式列表
    
    Returns:
        支持的格式列表
    """
    return JSONResponse({
        "success": True,
        "data": {
            "formats": processor.config.supported_formats,
            "output_formats": ["markdown", "html"]
        }
    })


@router.post("/test-upload")
async def test_upload():
    """
    测试上传接口是否正常工作
    
    Returns:
        测试结果
    """
    try:
        logger.info("测试上传接口")
        return JSONResponse({
            "success": True,
            "message": "上传接口正常工作",
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"测试上传接口失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




