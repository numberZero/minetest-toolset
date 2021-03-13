import glm
import os.path
import sqlite3

from . import base

class MapDatabase(base.MapDatabase):
	def __init__(self, world_path, readonly=False):
		db_path = os.path.join(world_path, 'map.sqlite')
		if readonly:
			from urllib.parse import quote
			url = f'file:{quote(db_path)}?mode=ro'
			self.db = sqlite3.connect(url, uri=True)
		else:
			self.db = sqlite3.connect(db_path)

	def close(self):
		self.db.close()

	def load_block(self, pos: glm.ivec3) -> bytes:
		cur = self.db.execute('SELECT data FROM blocks WHERE pos = ?', (self.block_pos_to_id(pos),))
		data, = cur.fetchone()
		cur.close()
		return data

	def save_block(self, pos: glm.ivec3, data: bytes) -> None:
		#with self.db:
		self.db.execute('REPLACE INTO blocks (pos, data) VALUES (?, ?)', (self.block_pos_to_id(pos), data)).close()

	def list_blocks(self) -> list[glm.ivec3]:
		cur = self.db.execute('SELECT pos FROM blocks')
		try:
			positions = []
			for key, in cur:
				positions.append(self.block_id_to_pos(key))
			return positions
		finally:
			cur.close()

	def iter_block_pos(self) -> list[glm.ivec3]:
		cur = self.db.execute('SELECT pos FROM blocks')
		try:
			for key, in cur:
				yield self.block_id_to_pos(key)
		finally:
			cur.close()

	def iter_blocks(self) -> list[glm.ivec3]:
		cur = self.db.execute('SELECT pos, data FROM blocks')
		try:
			for key, data in cur:
				yield self.block_id_to_pos(key), data
		finally:
			cur.close()
