from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# create a dummy user
User1 = User(name = "Jon Jones", email = "jjones@gmail.com", picture = "")
session.add(User1)
session.commit()


# items for first category
category1 = Category(user_id = 1, name = "Clothing")
session.add(category1)
session.commit()

categoryItem2 = CategoryItem(user_id = 1, name = "Warholsurf Skulls Boardshort", description = "Wild up top, mellow down low for a \
Warhol boardshort with a split personality.", price = "65.00", itemtype = "Clothing", category_item = category1)
session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(user_id = 1, name = "Men's Canyonlands's Hoodie", description = "Multi-pitch climbs in cool weather are no \
problem in this durable, smooth-face fleece hoodie crafted from stretch fabric so you won't sacrifice freedom of movement for \
warmth on the rock.", price = "85.00", itemtype = "Clothing", category_item = category1)
session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id = 1, name = "Men's Explore Tee", description = "Whether you're right side up or upside down, this breathable \
tee has got you covered.", price = "25.00", itemtype = "Clothing", category_item = category1)
session.add(categoryItem2)
session.commit()


# items for second category
category2 = Category(user_id = 1, name = "Shoes")
session.add(category2)
session.commit()

categoryItem1 = CategoryItem(user_id = 1, name = "Converse Chuck Taylor All Star", description = "The Chuck Taylors that never go out \
of style from the Converse collection. Chucks are classics and a wardrobe staple for all styles and ages.", price = "49.99", itemtype = "Shoes", category_item = category2)
session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(user_id = 1, name = "Merrel Men's All Out Blaze", description = "The fastest way to the top, this speed hiking shoe \
attacks terrain while allowing fluid, natural motion that responds to every contour for rapid agility. This show provides a \
comfortable glove like fit with a Bellows tongue to help keep the debris out.", price = "140.00", itemtype = "Shoes", category_item = category2)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id = 1, name = "Nike Men's Free Rn Flyknit", description = "Hit your health goal by sweating it out in the Nike Free Run \
running shoe.", price = "150.00", itemtype = "Shoes", category_item = category2)
session.add(categoryItem3)
session.commit()


# items for third category
category3 = Category(user_id = 1, name = "Accessories")
session.add(category3)
session.commit()

categoryItem1 = CategoryItem(user_id = 1, name = "Ray-Ban Aviator", description = "Ray-Ban is the world's most iconic eyewear brand \
and is a global leader in its sector. Every model in the Ray-Ban collection is the product of meticulous, original styling \
that translates the best of the latest fashion trends into an every-contemporary look for millions of Ray-Ban wearers around \
the world.", price = "115.00", itemtype = "Accessories", category_item = category3)
session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(user_id = 1, name = "Burberry Leather Belt", description = "Reversible belt featuring embossed check pattern. \
Made in Italy", price = "495.00", itemtype = "Accessories", category_item = category3)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id = 1, name = "RIP Coach Wallet", description = "Crafted in richly textured buffalo-embossed leather, this \
classic billfold is detailed with bold, baseball-inspired Rip and Repair stiching. Its slender, pocket-friendly design contains six \
card slots and a full-length bill compartment.", price = "150.00", itemtype = "Accessories", category_item = category3)
session.add(categoryItem3)
session.commit()


# items for fourth category
category4 = Category(user_id = 1, name = "Watches",)
session.add(category1)
session.commit()

categoryItem1 = CategoryItem(user_id = 1, name = "Casio G-Shock", description = "An all digital face, large size \
and wide face not only give a look of power and strength, but make it extremely easy-to-read and use \
with its oversized buttons.", price = "64.99", itemtype = "Watches", category_item = category4)
session.add(categoryItem1)
session.commit()


categoryItem2 = CategoryItem(user_id = 1, name = "Apple 42mm Smart Watch", description = "Stay connected in style with \
the Apple Watch Sport, which comes with a rose gold anodized aluminum chassis and a stone fluoroelastomer Sport \
band. Designed for users looking for the next generation of connectivity.", price = "306.99", itemtype = "Watches", category_item = category4)
session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(user_id = 1, name = "Michael Kors Men's Bradshaw Watch", description = "Menswear inspired details like \
a sporty, oversized chronograph dial give the black IP Michael Kors Bradshaw watch a bold look.", price = "122.95", itemtype = "Watches", category_item = category4)
session.add(categoryItem3)
session.commit()

print "added all items!"

