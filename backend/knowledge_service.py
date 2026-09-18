import os

from pypdf import PdfReader

from faiss_search import reload_knowledge
from logger import logger


def upload_knowledge_file(file, filename):
    logger.info(f"开始处理知识文件：{filename}")
    knowledge_dir = "knowledge"

    os.makedirs(knowledge_dir, exist_ok=True)

    # TXT 文件
    if filename.lower().endswith(".txt"):
        filepath = os.path.join(knowledge_dir, filename)

        content = file

        with open(filepath, "wb") as f:
            f.write(content)
        logger.info(f"TXT 文件保存成功：{filename}")

    # PDF 文件
    elif filename.lower().endswith(".pdf"):
        temp_path = os.path.join(knowledge_dir, filename)

        with open(temp_path, "wb") as f:
            f.write(file)

        reader = PdfReader(temp_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n\n"
        logger.info(f"PDF 文字提取完成：{filename}")
        if not text.strip():
            return {"error": "PDF 中没有提取到文字"}

        txt_filename = os.path.splitext(filename)[0] + ".txt"

        txt_path = os.path.join(knowledge_dir, txt_filename)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

    else:
        return {"error": "目前只支持 .txt 和 .pdf 文件"}

    # 重新建立 FAISS 索引
    logger.info("开始更新 FAISS 知识库")

    reload_knowledge()

    logger.info("FAISS 知识库更新完成")

    logger.info(f"知识文件处理完成：{filename}")
    return {"message": "知识文件上传成功", "filename": filename}
