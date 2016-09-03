# https://gist.github.com/alashow/07d9ef9c02ee697ab47d
chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',
        'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
        'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
        'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't',
        'u', 'v', 'x', 'y', 'z', '1', '2', '3'];

def encode(input):
	length = len(chars);
	encoded = "";

	if input < 0:
		input *= -1
		encoded += "-";

	if input == 0:
		return chars[0];

	while input > 0:
		val = int(input % length);
		input = int(input / length);
		encoded += chars[val];

	return encoded;

def decode(encoded):
	length = len(chars);
	decoded = 0;
	isNegative = 1;

	# if starts with minus, cut it and make result negative
	if encoded.startswith("-"):
		encoded = encoded[1:];
		isNegative = -1;

	for char in reversed(encoded):
		val = chars.index(char);
		decoded = (decoded * length) + val;

	return decoded * isNegative;