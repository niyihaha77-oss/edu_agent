# 打补丁 给数据库结构打补丁
"""
当我们的项目  已经有了数据库结构  而且我们想给数据库结构打补丁  添加新的表或者修改旧的表
比如  我们想给一个已经有的表  添加一个新字段  不会重新创建脚本
"""
from backend.dependencis import AsyncSessionLocal
from sqlalchemy import text

# 这些是一些处理的代码
_MIGRATIONS: list[tuple[str, str]] = [
    (
        "exam_submissions.weak_points",
        "ALTER TABLE exam_submissions ADD COLUMN IF NOT EXISTS weak_points JSONB",
    ),
    (
        "exam_reviews.knowledge_tag",
        "ALTER TABLE exam_reviews ADD COLUMN IF NOT EXISTS knowledge_tag VARCHAR(128)",
    ),
    (
        "exam_submissions.weak_points_summary",
        "ALTER TABLE exam_submissions ADD COLUMN IF NOT EXISTS weak_points_summary TEXT",
    ),
    (
        "idx_exam_submissions_student_created",
        "CREATE INDEX IF NOT EXISTS idx_exam_submissions_student_created "
        "ON exam_submissions (student_id, created_at DESC)",
    ),
    (
        "idx_resume_reviews_student_created",
        "CREATE INDEX IF NOT EXISTS idx_resume_reviews_student_created "
        "ON resume_reviews (student_id, created_at DESC)",
    ),
    (
        "idx_interview_sessions_student_created",
        "CREATE INDEX IF NOT EXISTS idx_interview_sessions_student_created "
        "ON interview_sessions (student_id, created_at DESC)",
    ),
]

# 这个函数在应用启动时执行补丁  init_db 相当于搭建一个项目的基本数据库
async def run_migrations():
    async with AsyncSessionLocal() as session:
        try:
            for name,sql in _MIGRATIONS:
                await session.execute(text(sql))
                await session.commit()
                pass
        except Exception:
            await session.rollback()
            raise