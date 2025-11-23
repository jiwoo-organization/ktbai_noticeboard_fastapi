from fastapi import HTTPException
from transformers import AutoTokenizer, AutoModelForCausalLM
from models.ai_model import CommentGenRequest
import torch

# 한국어 KoGPT-2 로드 (무료 + 로컬)
try:
    tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
    model = AutoModelForCausalLM.from_pretrained("skt/kogpt2-base-v2")
except Exception as e:
    raise RuntimeError(f"AI 모델 로딩 실패: {e}")


def generate_comment(data: CommentGenRequest):
    try:
        # 요청값 검증
        if not data.post_title.strip():
            raise HTTPException(status_code=400, detail="제목이 비어 있습니다.")
        if not data.post_content.strip():
            raise HTTPException(status_code=400, detail="내용이 비어 있습니다.")

        # 프롬프트 생성
        prompt = (
            f"제목: {data.post_title}\n"
            f"내용: {data.post_content}\n\n"
            "위 글에 자연스럽게 달릴 한국어 댓글 한 줄을 작성하세요:"
        )

        # 토크나이징
        inputs = tokenizer(prompt, return_tensors="pt")

        # 출력 토큰 개수(max_new_tokens)만 조절하면 안전함
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            do_sample=True,
            top_k=50,
            temperature=0.8
        )

        text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 프롬프트 이후의 결과만 추출
        if "작성하세요:" in text:
            text = text.split("작성하세요:")[1].strip()

        # 너무 길면 한 줄만 남기기
        text = text.split("\n")[0].strip()

        return {"comment": text}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 모델 오류: {str(e)}")
