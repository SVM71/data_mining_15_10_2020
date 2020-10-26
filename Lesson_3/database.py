from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

engine = create_engine('sqlite:///GB_Posts_train.db')
#engine = create_engine('mysql:///sqlalchemy_example.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

#models.Base.metadata.bind = engine

models.Base.metadata.create_all(bind = engine)

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
#session = DBSession()
# a1=models.Author(name='A1_nmae', url='a1_url')
# p1=models.Post(url='p1_url', img_url='pq_img_url', author_id=a1.id)
# p2=models.Post(url='p2_url', img_url='p2_img_url', author_id=a1.id)



if __name__ == '__main__':
    dbs = DBSession()
    print(1)


