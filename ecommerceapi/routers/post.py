import logging
from enum import Enum
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException

from ecommerceapi.database import comment_table, database, likes_table, post_table
from ecommerceapi.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes,
)
from ecommerceapi.models.user import User
from ecommerceapi.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# util para creat una estructura query SQL con sqlalchemy
select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(likes_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(likes_table))
    .group_by(post_table.c.id)
)


# funcion auxiliar
async def find_post(post_id: int):
    logger.info(f"Finding post with id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: User = Depends(get_current_user)
):  # dependence injection
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: User = Depends(get_current_user)
):  # dependence injection
    logger.info("Creating comment")
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, details="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    logger.info("Getting all posts")

    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    elif sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    elif sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("Getting comments for post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info("Getting post with comments")
    query = select_post_and_likes.where(post_table.c.id == post_id)
    post = await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("liking post")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**like.model_dump(), "user_id": current_user.id}
    query = likes_table.insert().values(data)

    logger.debug(query)

    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
