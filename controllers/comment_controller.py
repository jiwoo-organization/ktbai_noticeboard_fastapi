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
    # 필드 추출
    author = (data.get("author") or "익명").strip()
    content = (data.get("content") or "").strip()

    if not content:
        raise HTTPException(400, "댓글 내용을 입력해주세요.")

    new_comment = {
        "id": _next_comment_id(),
        "post_id": post_id,
        "author": author,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    comments.append(new_comment)
    return {"message": "댓글이 등록되었습니다.", "comment": new_comment}


def update_comment(post_id: int, comment_id: int, data: dict):
    # 대상 댓글 조회
    comment = next((c for c in comments if c["id"] == comment_id and c["post_id"] == post_id), None)
    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다.")

    # 작성자 검증(선택): 요청에 author가 왔는데 기존과 다르면 수정 불가
    req_author = (data.get("author") or "").strip()
    if req_author and req_author != comment["author"]:
        raise HTTPException(403, "작성자만 댓글을 수정할 수 있습니다.")

    # 내용 검증
    new_content = (data.get("content") or "").strip()
    if not new_content:
        raise HTTPException(400, "수정할 댓글 내용을 입력해주세요.")

    comment["content"] = new_content
    comment["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"message": "댓글이 수정되었습니다.", "comment": comment}


def delete_comment(post_id: int, comment_id: int, author: str | None = None):
    global comments

    # 대상 댓글 조회
    target = next((c for c in comments if c["id"] == comment_id and c["post_id"] == post_id), None)
    if not target:
        raise HTTPException(404, "삭제할 댓글이 없습니다.")

    # 작성자 검증(선택): author가 전달되면 일치해야 삭제 허용
    if author is not None and author.strip() and author.strip() != target["author"]:
        raise HTTPException(403, "작성자만 댓글을 삭제할 수 있습니다.")

    comments = [c for c in comments if not (c["id"] == comment_id and c["post_id"] == post_id)]
    return {"message": "댓글이 삭제되었습니다."}
