from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import *

engine = create_engine('sqlite:///blog.db', echo=False)
Base.metadata.create_all(bind=engine)
Maker = sessionmaker(bind=engine)


class Geek_blog:

    def get_writer(self, author_name: str, author_url: str, db: Maker) -> Writer:
        writer = db.query(Writer).filter(Writer.url == author_url).first()
        if not writer:
            writer = Writer(name=author_name, url=author_url)
            db.add(writer)
        return writer

    def save_to_db(self, page_data: dict, tags_list: list, comments_list: list) -> None:
        db = Maker()
        writer = self.get_writer(page_data['author_name'], page_data['author_url'], db)

        post = db.query(Post).filter(Post.url == page_data['page_url']).first()
        if not post:
            post = Post(url=page_data['page_url'], page_title=page_data['page_title'], img_url=page_data['img_url'],
                        publication_date=page_data['publication_date'], writer_id=writer.id, writer=writer,
                        author_name=page_data['author_name'])
            db.add(post)

        for tag_data in tags_list:
            tag = db.query(Tag).filter(Tag.name == tag_data['name']).first()
            if not tag:
                tag = Tag(name=tag_data['name'], url=tag_data['url'])
                post.tag.append(tag)

        for comment_data in comments_list:
            comment = db.query(Comment).filter(Comment.id == comment_data['id']).first()
            if not comment:
                comment = Comment(id=comment_data['id'], comment_text=comment_data['comment_text'])
                comment.writer = self.get_writer(comment_data['author_name'], comment_data['author_url'], db)
                post.comment.append(comment)

        db.commit()
        db.close()