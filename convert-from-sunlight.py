#!/usr/bin/python3

import sys
import contextlib
import struct
import zlib

import numpy as np
import glm

import database.sqlite

BATCH_SIZE = 1024

for world in sys.argv[1:]:
	with contextlib.closing(database.sqlite.MapDatabase(world)) as db:
		n = 0
		for pos, block_data in db.iter_blocks():
			# Заголовок
			version = block_data[0]
			if version < 29:
				continue # преобразовывать нечего
			if version > 29:
				raise NotImplementedError(f'Serialization version {version} is not supported. Supported versions: [22..29]')

			flags, lighting_completeness, content_item_size, params_item_size = struct.unpack('>BHBB', block_data[1:6])
			block_data = block_data[6:]
			if content_item_size != 2:
				raise NotImplementedError(f'Node type width {cw} not supported. Supported width: 2')
			if params_item_size != 2:
				raise NotImplementedError(f'Node param width {pw} not supported. Supported width: 2')

			# Блоки
			decomp = zlib.decompressobj()
			node_data = decomp.decompress(block_data)
			node_data += decomp.flush()
			block_data = decomp.unused_data
			if len(node_data) != 0x4000:
				raise ValueError(f'Wrong block content size: {len(node_data)}')
			# Метаданные
			# Таймеры (v24)
			# Статические объекты
			# Время изменения
			# name-id
			# Таймеры (v25+)

			param0 = node_data[:0x2000]
			param1 = node_data[0x2000:0x3000]
			param2 = node_data[0x3000:]
			#param0 = np.frombuffer(param0, dtype='>H').reshape((16, 16, 16))
			param1 = np.frombuffer(param1, dtype='B').reshape((16, 16, 16))
			#param2 = np.frombuffer(param2, dtype='B').reshape((16, 16, 16))
			sun = param1 & 0x0f
			art = param1 >> 4
			day = np.fmax(sun, art)
			night = art
			new_param1 = day | (night << 4)
			new_node_data = param0 + new_param1.tobytes() + param2
			assert(len(new_node_data) == 0x4000)

			new_version = 28
			new_block_data = struct.pack('>BBHBB', new_version, flags, lighting_completeness, content_item_size, params_item_size)
			new_block_data += zlib.compress(new_node_data)
			new_block_data += block_data

			db.save_block(pos, new_block_data)
			n += 1
			if n % BATCH_SIZE == 0:
				print(f'Converted {n} blocks, committing...')
				db.db.commit()
		print(f'Converted {n} blocks, committing...')
		db.db.commit()
		print(f'Done. {n} blocks converted')
