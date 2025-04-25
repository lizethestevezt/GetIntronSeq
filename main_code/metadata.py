import sqlalchemy as sql

metadata = sql.MetaData()

# Table for storing genes per contig
genes = sql.Table(
    "genes", metadata,
    sql.Column("id", sql.Integer, primary_key=True, autoincrement=True),
    sql.Column("contig", sql.String, nullable=False),
    sql.Column("gene", sql.String, nullable=False)
)

# Table for storing introns per gene
introns = sql.Table(
    "introns", metadata,
    sql.Column("id", sql.Integer, primary_key=True, autoincrement=True),
    sql.Column("gene", sql.String, nullable=False),
    sql.Column("intron", sql.String, nullable=False),
    sql.Column("beg", sql.Integer, nullable=False),
    sql.Column("end", sql.Integer, nullable=False),
    sql.Column("seq", sql.String, nullable=True),
    sql.Column("ori", sql.String, nullable=True),
    sql.Column("obs", sql.String, nullable=True)
)