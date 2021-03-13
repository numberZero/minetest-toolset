import glm

class MapDatabase:
	def save_block(self, pos: glm.ivec3, data: bytes) -> None: raise NotImplementedError()
	def load_block(self, pos: glm.ivec3) -> bytes: return None
	def delete_block(self, pos: glm.ivec3) -> None: raise NotImplementedError()
	def list_blocks(self) -> list[glm.ivec3]: return []

	@classmethod
	def block_pos_to_id(cls, pos: glm.ivec3) -> int:
		pos = glm.ivec3(pos)
		assert(all(abs(pos) < glm.ivec3(0x800)))
		u64 = lambda x: x & 0xffff_ffff_ffff_ffff
		s64 = lambda x: (x & 0x7fff_ffff_ffff_ffff) - (x & 0x8000_0000_0000_0000)
		return s64(
				u64(pos.z) * 0x1_000_000 + \
				u64(pos.y) * 0x1_000 + \
				u64(pos.x)
				)

	@classmethod
	def block_id_to_pos(cls, id: int) -> glm.ivec3:
		unsigned_to_signed = lambda x: x if x < 0x800 else x - 0x1000
		i = id
		x = unsigned_to_signed(i % 0x1000)
		j = (i - x) // 0x1000
		y = unsigned_to_signed(j % 0x1000)
		k = (j - y) // 0x1000
		z = unsigned_to_signed(k % 0x1000)
		return glm.ivec3(x, y, z)

if __name__ == '__main__':
	for pos in [
			(0, 0, 0), (1, 2, 3),
			(-1, 2, 3), (1, -2, 3), (1, 2, -3),
			(0x7FF, 2, -3), (1, 0x7FF, 3), (1, 4, 0x7FF),
			(-0x7FF, 2, -3), (1, -0x7FF, 3), (1, -4, -0x7FF),
			]:
		key = MapDatabase.block_pos_to_id(pos)
		print(f'{pos} -> {key}')
		assert(MapDatabase.block_id_to_pos(key) == pos)
