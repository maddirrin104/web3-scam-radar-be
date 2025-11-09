from alembic import op


op.create_table('policy_snapshots',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('etag', sa.String(64), nullable=False),
sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
sa.Column('payload', JSONB, nullable=False),
sa.UniqueConstraint('etag')
)


op.create_table('domain_reputation',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('domain', sa.String(255), nullable=False),
sa.Column('risk', sa.Integer(), nullable=False, server_default='0'),
sa.Column('labels', JSONB, server_default=sa.text("'{}'::jsonb")),
sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
sa.UniqueConstraint('domain', name='uq_domain')
)
op.create_index('ix_domain', 'domain_reputation', ['domain'])


op.create_table('contract_reputation',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('chain_id', sa.BigInteger(), nullable=False),
sa.Column('address', sa.String(64), nullable=False),
sa.Column('verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
sa.Column('risk', sa.Integer(), nullable=False, server_default='0'),
sa.Column('labels', JSONB, server_default=sa.text("'{}'::jsonb")),
sa.UniqueConstraint('chain_id','address', name='uq_chain_addr')
)
op.create_index('ix_contract_combo', 'contract_reputation', ['chain_id','address'])


op.create_table('fourbyte',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('selector', sa.String(10), nullable=False),
sa.Column('signature', sa.String(255), nullable=False),
sa.UniqueConstraint('selector', name='uq_selector')
)


op.create_table('alert_logs',
sa.Column('id', sa.Integer(), primary_key=True),
sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
sa.Column('tab_domain', sa.String(255), nullable=False),
sa.Column('chain_id', sa.BigInteger(), nullable=False),
sa.Column('contract', sa.String(64), nullable=False),
sa.Column('selector', sa.String(10), nullable=False),
sa.Column('risk', sa.Integer(), nullable=False),
sa.Column('verdict', sa.String(32), nullable=False),
sa.Column('reason', sa.String(512), nullable=False),
sa.Column('raw', JSONB, server_default=sa.text("'{}'::jsonb"))
)


def downgrade():
op.drop_table('alert_logs')
op.drop_table('fourbyte')
op.drop_index('ix_contract_combo', table_name='contract_reputation')
op.drop_table('contract_reputation')
op.drop_index('ix_domain', table_name='domain_reputation')
op.drop_table('domain_reputation')
op.drop_table('policy_snapshots')
op.drop_table('rules')