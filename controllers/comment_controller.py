from fastapi import HTTPException
from datetime import datetime

comments = [
    {"id": 1, "post_id": 1, "author": "Bob", "content": "좋은 글이에요!", "created_at": "2025-11-11 12:00:00"},
]

def _next_comment_id():
    return max([c["id"] for c in comments], default=0) + 1


def get_comments(post_id: int):
    post_comments = [c for c in comments if c["post_id"] == post_id]
    return {"count": len(post_comments), "comments": post_comments}


def add_comment(post_id: int, data: dict):
    content = data.get("content", "").strip()
    if not content:
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    new_comment = {
        "id": _next_comment_id(),
        "post_id": post_id,
        "author": data.get("author", "익명"),
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    comments.append(new_comment)
    return {"message": "댓글이 등록되었습니다.", "comment": new_comment}


def update_comment(post_id: int, comment_id: int, data: dict):
    comment = next((c for c in comments if c["id"] == comment_id and c["post_id"] == post_id), None)
    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")
    comment["content"] = data.get("content", comment["content"])
    return {"message": "댓글이 수정되었습니다.", "comment": comment}


def delete_comment(post_id: int, comment_id: int):
    global comments
    before = len(comments)
    comments = [c for c in comments if not (c["id"] == comment_id and c["post_id"] == post_id)]
    if len(comments) == before:
        raise HTTPException(404, "삭제할 댓글이 없습니다.")
    return {"message": "댓글이 삭제되었습니다."}
