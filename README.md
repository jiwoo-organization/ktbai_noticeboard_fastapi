# 아무말 대잔치 백엔드
## 기술 스택
- Python
- FastAPI
- SQLAlchemy ORM
- SQLite (로컬 개발용)
- MySQL
- JWT authentication
- CORS Middleware
- Multipart File Upload
- HuggingFace Transformers (KoGPT-2 사용)

## API 엔드 포인트
### Users API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/users/register` | 회원가입 |
| POST | `/api/users/login` | 로그인 (JWT 발급) |
| PUT  | `/api/users/me/profile` | 프로필 수정 |
| PUT  | `/api/users/me/password` | 비밀번호 변경 |

### Posts API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/posts` | 게시글 전체 조회 |
| GET | `/api/posts/{post_id}` | 게시글 상세 조회 |
| POST | `/api/posts` | 게시글 작성 (파일 업로드 포함) |
| PUT | `/api/posts/{post_id}` | 게시글 수정 |
| DELETE | `/api/posts/{post_id}` | 게시글 삭제 |
| POST | `/api/posts/{post_id}/like` | 좋아요 토글 |

### Comments API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/posts/{post_id}/comments` | 댓글 리스트 조회 |
| POST | `/api/posts/{post_id}/comments` | 댓글 작성 |
| PUT | `/api/posts/{post_id}/comments/{comment_id}` | 댓글 수정 |
| DELETE | `/api/posts/{post_id}/comments/{comment_id}` | 댓글 삭제 |

### AI API
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/ai/generate-comment` | KoGPT-2 기반 자동 댓글 생성 |

## 주요 기능 요약
✔ JWT 로그인 인증
- 로그인 성공 시 access token 발급
- Authorization: Bearer 토큰 사용
  
✔ 게시글 CRUD
- 이미지 업로드 가능 (uploads 폴더 저장)
- 작성자 본인만 수정/삭제 가능

✔ 댓글 CRUD
- 작성자 본인만 수정/삭제 가능

✔ 좋아요 토글
- 좋아요 / 취소 자동 처리

✔ AI 자동 댓글 생성
- 게시글 작성 시 KoGPT-2가 댓글을 1개 자동 생성하여 DB 저장
  
## 트러블 슈팅
- 문제: 게시글 이미지 경로 로드 실패
- 해결: 이미지 URL을 /uploads/...로 반환하도록 통일

- 문제: 권한 검사 오류
- 해결: user.nickname과 author 비교 시 trim 적용
