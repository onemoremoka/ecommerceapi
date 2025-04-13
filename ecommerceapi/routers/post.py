from fastapi import APIRouter, HTTPException

from ecommerceapi.models.post import Comment, CommentIn, UserPost, UserPostIn

router = APIRouter()

post_table = {}
comment_table = {}


def find_post(post_id: int):
    return comment_table.get(post_id)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    last_record_id = len(post_table)
    register = {**data, "id": last_record_id}
    post_table[last_record_id] = register
    return register


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, details="Post not found")
    data = comment.model_dump()
    last_record_id = len(data)
    register = {**data, "id": last_record_id}
    comment_table[last_record_id] = register
    return register


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    return list(post_table.values())


# @router.get("/post/{post_id}/comment", response_model=list[Comment])
# async def get_comments_on_post(post_id: int):
#     query = comment_table.select().where(comment_table.c.post_id == post_id)
#     return await database.fetch_all(query)
