from __future__ import division
import cv2
import numpy as np
import os
import sys
import random
import copy

LINE_HEIGHT = 15
CHAR_HEIGHT_SHIFT = 7

#placing signs on template after lines are placed
def place_signs(black_board, char_height, num_lines, line_coord, sign_imgs):
	#removing the excess padding in the sign images, top/bottom/sides
	def trim_edges(character):
		row_index = []
		col_index = []
		# alternative :np.where(~a.any(axis=1))[0]
		for i in range(0, character.shape[0]):
			row = character[i,:]
			if np.max(row) > 0:
				break
			row_index.append(i)

		for i in xrange(character.shape[0]-1, -1, -1):
			row = character[i,:]
			if np.max(row) > 0:
				break
			row_index.append(i)

		del_count = 0
		row_index = sorted(row_index)
		#deleting the rows(top/bottom)
		for row in row_index:
			character = np.delete(character, (row - del_count), axis=0)
			del_count += 1

		for j in range(0, character.shape[1]):
			col = character[:,j]
			if np.max(col) > 0:
				break
			col_index.append(j)

		for i in xrange(character.shape[1]-1, -1, -1):
			col = character[:,j]
			if np.max(col) > 0:
				break
			col_index.append(j)

		del_count = 0
		col_index = sorted(col_index)
		#deleting the columns(sides)
		for col in col_index:
			character = np.delete(character, (col - del_count), axis=1)
			del_count += 1

		return character
	#draw character on to the template
	def draw_char(black_board, y_offset):
		remaining_width = black_board.shape[1]
		list_chars = []

		#fill the lines with characters, and find excess padding in the line
		while remaining_width > 0:
			sign_img = random.sample(sign_imgs, k=1)
			image = cv2.imread(sign_img[0], cv2.IMREAD_GRAYSCALE)
			image = trim_edges(image)
			char_width = int(image.shape[1] * ( char_height / image.shape[0] ))
			if (remaining_width - char_width) < 0:
				break
			resized = cv2.resize(image, (char_width, char_height), interpolation = cv2.INTER_AREA)		
			list_chars.append(resized)
			remaining_width = remaining_width - char_width

		x_offset = 0
		#use the excess padding for each character's left margin
		for img in list_chars:
			if random.randint(0, 2): # 1 in 3 characters will be ignored
				left_margin = random.randint(0, remaining_width)
				remaining_width -= left_margin
				x_offset += left_margin
				for i in range(y_offset, y_offset+img.shape[0]):
					for j in range(x_offset, x_offset + img.shape[1]):
						val = max(img[i-y_offset][j-x_offset], black_board[i,j])
						black_board[i,j] = val
				x_offset += img.shape[1]

		return black_board

	char_height -= (LINE_HEIGHT + CHAR_HEIGHT_SHIFT)
	line_coord = [0] + line_coord + [black_board.shape[0]]
	partition_height = [line_coord[i] - line_coord[i-1] for i in range(1, len(line_coord))]

	#adding characters in each line, also check if each partition allows multiple characters
	for i in range(0,len(partition_height)):
		if char_height * 2 < partition_height[i]:
			num_rows = int(partition_height[i] / char_height)
			for r in range(0,num_rows):
				if random.randint(0, 2): # 1 in 3 lines will be ignored
					y = int(line_coord[i] + ((partition_height[i] * (r*2+1)) / (num_rows*2)) - (char_height / 2))
					black_board = draw_char(black_board, y)

		else:
			y = int(line_coord[i] + (partition_height[i] / 2) - (char_height / 2))
			black_board = draw_char(black_board, y)

	return black_board

#draw the lines on the template
def place_lines(black_board, line_imgs, num_lines, max_line):

	top = 0
	char_height = int(black_board.shape[0] / (max_line + 1))
	line_coord = []
	for i in range(0,num_lines):

		line_img = random.sample(line_imgs, k=1)
		image = cv2.imread(line_img[0], cv2.IMREAD_GRAYSCALE)
	
		width = black_board.shape[1]
		height = LINE_HEIGHT
		dim = (width, height)
		resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
		top += char_height
		bottom = black_board.shape[0] - (char_height * (num_lines - i))

		y_offset = random.randint(top, bottom)
		black_board[y_offset:y_offset+resized.shape[0],0:resized.shape[1]] = resized
		line_coord.append(y_offset)
		top = y_offset
	
	return black_board, char_height, line_coord

#output the number of lines to be drawn on the template depending on template size
#you can change the probablities of the number of lines to be drawn while generating templates
def get_num_lines(dim):
	if dim == (400,490):
		num_lines = random.sample([2]+[3]+[4]*3+[5]*5+[6]*6, k=1)[0]
		max_line = 6
	elif dim == (496,520):
		num_lines = random.sample([2]+[3]+[4]*3+[5]*5+[6]*6+[7]*7, k=1)[0]
		max_line = 7
	elif dim == (614,907):
		num_lines = random.sample([2]+[3]+[4]*2+[5]*3+[6]*2+[7]*4+[8]*4+[9]*4+[10]*5+[11]*4+[12]*5+[13]*6, k=1)[0]
		max_line = 13
	elif dim == (760,890):
		num_lines = random.sample([2]+[3]+[4]*2+[5]*2+[6]*5+[7]*6+[8]*4+[9]*5+[10]*7, k=1)[0]
		max_line = 10
	return num_lines, max_line


def get_sub_dir(path):
	temp_list = []
	for r, d, f in os.walk(path):
		for directory in d:
			temp_list.append(directory)
		break
	return temp_list

def get_images(root):
	imgs = []
	line_subdir = get_sub_dir(root)

	for ld in line_subdir:
		for r, d, f in os.walk(os.path.join(root,ld)):
			for file in f:
				imgs.append(os.path.join(root,ld,file))
			break
	return imgs

def main():

	sign_imgs = get_images("./input/signs/")
	line_imgs = get_images("./input/line/")

	#change dimensions according to the 3d model
	bb_dimensions = [[400,490]] #,[496,520],[614,907],[760,890]
	bb_dimensions_s = random.sample(bb_dimensions, k=1)
	bb_width = bb_dimensions_s[0][0]
	bb_height = bb_dimensions_s[0][1]
	
	for i in range(0,11):
		num_lines, max_line = get_num_lines((bb_width, bb_height))

		black_board = np.zeros((bb_height,bb_width), np.uint8)

		black_board, char_height, line_coord = place_lines(black_board, line_imgs, num_lines, max_line)
		black_board = place_signs(black_board, char_height, num_lines, line_coord, sign_imgs)
		
		cv2.imwrite("./input/templates/400x490/template_" + str(i) + ".png", black_board)
	
if __name__ == "__main__":
	sys.exit(main())