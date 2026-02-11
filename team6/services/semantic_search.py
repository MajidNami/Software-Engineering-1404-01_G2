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

#         vectorstore = FAISS.from_texts(documents, self.embeddings)

#         results = vectorstore.similarity_search_with_score(translated_query, k=k)

#         # برگرداندن مقاله‌ها به ترتیب شباهت معنایی
#         ranked_articles = []
#         for doc, score in results:
#             index = documents.index(doc.page_content)
#             ranked_articles.append((articles[index], score))

#         return ranked_articles


import os
import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from deep_translator import GoogleTranslator

# تنظیمات لاگر برای مشاهده وضعیت در ترمینال
logger = logging.getLogger(__name__)

def simple_normalize(text: str) -> str:
    """نرمال‌سازی مقدماتی متن برای حذف تداخل کاراکترهای عربی و فارسی"""
    if not text:
        return ""
    return (
        text.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("‌", " ")
            .strip()
    )

class SemanticSearchService:
    def __init__(self):
        # پیدا کردن مسیر پوشه اپلیکیشن team6 برای ذخیره ایندکس
        # __file__ آدرس فایل فعلی است، پس dirname آن می‌شود پوشه services و dirname بعدی می‌شود پوشه team6
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.index_path = os.path.join(os.path.dirname(current_dir), "faiss_index")
        
        # لود مدل امبدینگ (این مدل چندزبانه است و در رم لود می‌شود)
        logger.info("Loading HuggingFace Embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vectorstore = self._load_index()

    def _load_index(self):
        """تلاش برای بارگذاری ایندکس از فایل محلی در پوشه team6"""
        if os.path.exists(self.index_path):
            try:
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                return FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                logger.error(f"Error loading index: {e}")
        return None

    def build_index(self, articles):
        """ترجمه مقالات و ساخت ایندکس برای اولین بار"""
        if not articles:
            return None
        
        logger.info("🚀 Building semantic index. This may take a minute (translating articles)...")
        
        documents = []
        metadatas = []
        translator = GoogleTranslator(source='fa', target='en')

        for a in articles:
            try:
                # ترکیب تایتل، خلاصه و بخشی از متن برای ترجمه و ایندکس
                full_text_fa = f"{a.title_fa} {a.summary or ''} {a.body_fa[:400]}"
                # ترجمه به انگلیسی برای بالا رفتن دقت مدل چندزبانه
                translated_text = translator.translate(full_text_fa)
                
                documents.append(simple_normalize(translated_text))
                metadatas.append({"id": str(a.id)}) 
            except Exception as e:
                logger.warning(f"Skipping article {a.id} due to error: {e}")
                continue

        if not documents:
            return None

        # ساخت ایندکس FAISS
        vectorstore = FAISS.from_texts(documents, self.embeddings, metadatas=metadatas)
        
        # ذخیره در پوشه team6/faiss_index
        vectorstore.save_local(self.index_path)
        self.vectorstore = vectorstore
        logger.info(f"✅ Index built and saved to {self.index_path}")
        return vectorstore

    def search(self, articles, query, k=10):
        """
        جستجوی معنایی بین مقالات
        articles: کوئری‌ست مقالات جنگو
        query: متن جستجوی کاربر
        k: تعداد نتایج
        """
        # اگر ایندکس وجود ندارد، همین حالا آن را بساز
        if self.vectorstore is None:
            self.build_index(articles)
        
        if not self.vectorstore:
            return []

        # ۱. ترجمه کوئری کاربر به انگلیسی
        try:
            translated_query = GoogleTranslator(source='fa', target='en').translate(query)
        except Exception:
            translated_query = query

        # ۲. جستجوی شباهت (خروجی: لیست داکیومنت‌ها و امتیاز فاصله)
        # نکته: در FAISS هرچه Score کمتر باشد (نزدیک به صفر)، شباهت بیشتر است.
        results = self.vectorstore.similarity_search_with_score(translated_query, k=k)

        # ۳. پیدا کردن مدل‌های جنگو بر اساس IDهای ذخیره شده در متادیتا
        ranked_articles = []
        article_dict = {str(a.id): a for a in articles}
        
        # حد آستانه برای شباهت (قابل تنظیم: معمولاً بین 0.4 تا 0.8)
        # هرچه این عدد کمتر باشد، جستجو سخت‌گیرانه‌تر می‌شود.
        DISTANCE_THRESHOLD = 0.6 

        for doc, score in results:
            if score <= DISTANCE_THRESHOLD:
                article_id = doc.metadata.get("id")
                if article_id in article_dict:
                    ranked_articles.append((article_dict[article_id], score))

        return ranked_articles