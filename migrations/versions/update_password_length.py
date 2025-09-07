"""update password length

Revision ID: update_password_length
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_password_length'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Modifica la lunghezza del campo password
    op.alter_column('utente', 'password',
                    existing_type=sa.String(128),
                    type_=sa.String(512),
                    existing_nullable=False)
    
    # Aggiorna anche i campi nome e cognome
    op.alter_column('utente', 'nome',
                    existing_type=sa.String(64),
                    type_=sa.String(50),
                    existing_nullable=True,
                    nullable=False)
    op.alter_column('utente', 'cognome',
                    existing_type=sa.String(64),
                    type_=sa.String(50),
                    existing_nullable=True,
                    nullable=False)

def downgrade():
    # Ripristina la lunghezza originale del campo password
    op.alter_column('utente', 'password',
                    existing_type=sa.String(512),
                    type_=sa.String(128),
                    existing_nullable=False)
    
    # Ripristina i campi nome e cognome
    op.alter_column('utente', 'nome',
                    existing_type=sa.String(50),
                    type_=sa.String(64),
                    existing_nullable=False,
                    nullable=True)
    op.alter_column('utente', 'cognome',
                    existing_type=sa.String(50),
                    type_=sa.String(64),
                    existing_nullable=False,
                    nullable=True) 