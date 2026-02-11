# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from deep_translator import GoogleTranslator


# def simple_normalize(text: str) -> str:
#     return (
#         text.replace("ي", "ی")
#             .replace("ك", "ک")
#             .replace("‌", " ")
#             .strip()
#     )


# class SemanticSearchService:
#     def __init__(self):
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
#         )

#     def search(self, articles, query, k=10):
#         """
#         articles: list[WikiArticle]
#         query: str
#         """

#         if not articles:
#             return []
#         translated_query = GoogleTranslator(source='fa', target='en').translate(query)
#         documents = [
#             simple_normalize(
#                 f"{GoogleTranslator(source='fa', target='en').translate(a.title_fa) or ''} {GoogleTranslator(source='fa', target='en').translate(a.summary) or ''} {GoogleTranslator(source='fa', target='en').translate(a.body_fa) or ''}"
#             )
#             for a in articles
#         ]

#         print("translation completed, building FAISS index...")
#         vectorstore = FAISS.from_texts(documents, self.embeddings)
#         print("Saving FAISS index locally...")
#         vectorstore.save_local("faiss_index_directory")
#         print("FAISS index saved to 'faiss_index_directory'") 

#         results = vectorstore.similarity_search_with_score(translated_query, k=k)
#         print("result calculated")

#         # برگرداندن مقاله‌ها به ترتیب شباهت معنایی
#         ranked_articles = []
#         for doc, score in results:
#             index = documents.index(doc.page_content)
#             ranked_articles.append((articles[index], score))

#         return ranked_articles

import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from deep_translator import GoogleTranslator

class SemanticSearchService:
    def __init__(self):
        # آدرس پوشه ذخیره‌سازی
        self.index_path = "team6\\faiss_index_directory"
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        # بارگذاری ایندکس در صورت وجود
        self.vectorstore = self._load_index()

    def simple_normalize(text: str) -> str:
        return (
            text.replace("ي", "ی")
                .replace("ك", "ک")
                .replace("‌", " ")
                .strip()
        )

    def _load_index(self):
        if os.path.exists(self.index_path):
            print("✅ ایندکس پیدا شد. در حال بارگذاری...")
            return FAISS.load_local(
                self.index_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
        return None

    def search(self, articles, query, k=10):
        if not articles: return []

        # ۱. ترجمه کوئری
        translated_query = GoogleTranslator(source='fa', target='en').translate(query)

        # ۲. ساخت ایندکس (فقط اگر لود نشده باشد)
        if self.vectorstore is None:
            print("⚠️ ایندکس پیدا نشد یا ناقص است. در حال ساخت ایندکس جدید با متادیتا...")
            documents = []
            metadatas = []
            
            for a in articles:
                print("debug -1")
                print(f"title is{a.title_en}, body is {a.body_en}")
                text = f"{a.title_en or ''} {a.body_en or ''}"
                print("debug0")
                # translated_text = GoogleTranslator(source='fa', target='en').translate(text)
                
                documents.append(text)
                # ذخیره ID مقاله در متادیتا (این بخش در فایل قبلی شما نبود)
                metadatas.append({"id": a.id_article})
                print("debug1")
            self.vectorstore = FAISS.from_texts(documents, self.embeddings, metadatas=metadatas)
            self.vectorstore.save_local(self.index_path)
            print("✅ ایندکس با موفقیت ساخته و ذخیره شد.")

        # ۳. جستجو
        results = self.vectorstore.similarity_search_with_score(translated_query, k=k)

        # ۴. بازیابی مقالات با استفاده از متادیتای ذخیره شده در فایل
        ranked_articles = []
        article_map = {a.id_article: a for a in articles}
        
        for doc, score in results:
            article_id = doc.metadata.get("id") # ID را از دل فایل لود شده می‌کشد
            if article_id in article_map:
                ranked_articles.append((article_map[article_id], score))

        return ranked_articles
