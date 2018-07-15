from __future__ import print_function
from ethereum import utils
import bitcoin as b

from .utils import tobe256, bytes_to_int, randb256


def pack_signature(v, r, s):
	"""
	This saves a byte by using the last bit of `s` to store `v`
	This allows the signature to be packed into two 256bit words
	This is possible because `s` is mod `N`, and the highest bit 
	doesn't seem to be used...

	Having put it through a SAT solver it's 100% possible for this
	bit to be set, but in reality it's very unlikely that this
	fails, whereas packing it into the `r` value fails 50% of the
	time as you'd expect....
	"""
	assert v == 27 or v == 28
	v = (v - 27) << 255
	return tobe256(r), tobe256(s | v)


def unpack_signature(r, sv):
	sv = bytes_to_int(sv)
	if (sv & (1 << 255)):
		v = 28
		sv = sv ^ (1 << 255)
	else:
		v = 27
	return v, bytes_to_int(r), sv


def pubkey_to_ethaddr(pubkey):
	if isinstance(pubkey, tuple):
		assert len(pubkey) == 2
		pubkey = b.encode_pubkey(pubkey, 'bin')
	return utils.sha3(pubkey[1:])[12:].encode('hex')


def sign(messageHash, key):
	return pack_signature(*b.ecdsa_raw_sign(messageHash, seckey))


def recover(messageHash, r, sv):
	 return pubkey_to_ethaddr(b.ecdsa_raw_recover(messageHash, unpack_signature(r, sv)))


if __name__ == "__main__":
	while True:
		messageHash = randb256()
		seckey = randb256()
		pubkey = pubkey_to_ethaddr(b.privtopub(seckey))

		sig_t = b.ecdsa_raw_sign(messageHash, seckey)
		sig = sign(messageHash, seckey)
		assert unpack_signature(*sig) == sig_t

		pubkey_v = recover(messageHash, *sig)
		"""print("Pubkey:", pubkey_v, pubkey)
		print("Message:", messageHash.encode('hex'))
		print("Sig:", sig[0].encode('hex'), sig[1].encode('hex'))"""
		assert pubkey == pubkey_v



