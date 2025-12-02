import re
from typing import Tuple, Optional

def parse_document_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """解析飞书文档 URL，返回 token 和类型
    
    支持的 URL 格式：
    - https://{domain}/docx/{token} -> (token, 'docx')
    - https://{domain}/wiki/{token} -> (token, 'wiki')
    - https://{domain}/sheets/{token} -> (token, 'sheet')
    - https://{domain}/base/{token} -> (token, 'bitable')
    - https://{domain}/docs/{token} -> (token, 'doc')
    
    Args:
        url (str): 飞书文档 URL
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (token, type)
        如果无法解析，返回 (None, None)
        type 可能的值: 'docx', 'wiki', 'sheet', 'bitable', 'doc'
    """
    if not url:
        return None, None
        
    # 定义正则匹配模式
    patterns = [
        (r'/docx/([a-zA-Z0-9]+)', 'docx'),
        (r'/wiki/([a-zA-Z0-9]+)', 'wiki'),
        (r'/sheets/([a-zA-Z0-9]+)', 'sheet'),
        (r'/base/([a-zA-Z0-9]+)', 'bitable'),
        (r'/docs/([a-zA-Z0-9]+)', 'doc'),
    ]
    
    for pattern, doc_type in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), doc_type
            
    return None, None
