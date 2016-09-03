def encode(input, chars):
	length = len(chars);
	encoded = "";

	if input == 0:
		return chars[0];

	while input > 0:
		val = int(input % length);
		input = int(input / length);
		encoded += chars[val];

	return encoded;

def decode(encoded, map):
	length = len(chars);
	decoded = 0;

	for char in reversed(encoded):
		val = chars.index(char);
		decoded = (decoded * length) + val;

	return decoded;

chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',
        'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
        'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
        'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't',
        'u', 'v', 'x', 'y', 'z', '1', '2', '3'];

print encode(101310211, chars);
print decode("WYDEW", chars);
