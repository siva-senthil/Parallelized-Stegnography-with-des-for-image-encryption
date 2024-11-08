import click
from PIL import Image
import time
from threading import Thread
import matplotlib.pyplot as plt
import os
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

class Steganography(Thread):
    @staticmethod
    def __int_to_bin(rgb):
        r, g, b = rgb
        return (f'{r:08b}', f'{g:08b}', f'{b:08b}')

    @staticmethod
    def __bin_to_int(rgb):
        r, g, b = rgb
        return (int(r, 2), int(g, 2), int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4], g1[:4] + g2[:4], b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])
                rgb2 = Steganography.__int_to_bin((0, 0, 0))
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])
                rgb = Steganography.__merge_rgb(rgb1, rgb2)
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img_path):
        img = Image.open(img_path)
        pixel_map = img.load()
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])
                rgb = (r[4:] + '0000', g[4:] + '0000', b[4:] + '0000')
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))
        return new_image

    @staticmethod
    def encrypt_image(img_path, key):
        with open(img_path, 'rb') as img_file:
            img_data = img_file.read()
        cipher = DES.new(key, DES.MODE_CBC)
        encrypted_data = cipher.iv + cipher.encrypt(pad(img_data, DES.block_size))
        return encrypted_data

    @staticmethod
    def decrypt_image(encrypted_data, key):
        iv = encrypted_data[:8]
        encrypted_data = encrypted_data[8:]
        cipher = DES.new(key, DES.MODE_CBC, iv=iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), DES.block_size)
        return decrypted_data

def main():
    choice = int(input(":: Welcome to Steganography ::\n1. Encrypt and Merge\n2. Unmerge and Decrypt\n"))
    threads = []
    key = b'12345678'  # DES key

    # Ensure output directories exist
    os.makedirs('resultoutpar', exist_ok=True)
    os.makedirs('encrypted', exist_ok=True)
    os.makedirs('decrypted', exist_ok=True)
    os.makedirs('decodepar', exist_ok=True)

    if choice == 1:
        mapp = []
        timeencodeserial = 0
        for i in range(10):
            threads.append(Steganography())

        for i, t in enumerate(threads):
            t.start()
            img1 = f'big/b{i}.png'
            img2 = f'small/s{i}.png'
            output = f'resultoutpar/rr{i}.png'
            encrypted_img2 = Steganography.encrypt_image(img2, key)
            encrypted_img2_path = f'encrypted/encrypted_s{i}.bin'
            with open(encrypted_img2_path, 'wb') as enc_file:
                enc_file.write(encrypted_img2)

            start = time.time()
            merged_img = Steganography.merge(Image.open(img1), Image.open(img2))
            merged_img.save(output)
            end = time.time()
            timeencodeserial += end - start
            mapp.append(int(end - start))

        for t in threads:
            t.join()

        plt.xlabel('Number of images')
        plt.ylabel('Parallel Time')
        plt.title(f"Time to encode 10 parallel images: {timeencodeserial}")
        plt.scatter(range(1, 11), mapp)
        plt.show()

    elif choice == 2:
        mapp = []
        timeencodeserial = 0
        for i in range(10):
            threads.append(Steganography())

        for i, t in enumerate(threads):
            t.start()
            img3 = f'resultoutpar/rr{i}.png'
            output1 = f'decodepar/dd{i}.png'
            encrypted_img_path = f'encrypted/encrypted_s{i}.bin'
            with open(encrypted_img_path, 'rb') as enc_file:
                encrypted_data = enc_file.read()

            decrypted_data = Steganography.decrypt_image(encrypted_data, key)
            decrypted_image_path = f'decrypted/decrypted_s{i}.png'
            with open(decrypted_image_path, 'wb') as dec_file:
                dec_file.write(decrypted_data)

            start = time.time()
            unmerged_image = Steganography.unmerge(img3)
            unmerged_image.save(output1)
            end = time.time()
            timeencodeserial += end - start
            mapp.append(int(end - start))

        for t in threads:
            t.join()

        plt.xlabel('Number of images')
        plt.ylabel('Parallel Time')
        plt.title(f"Time to decode 10 parallel images: {timeencodeserial}")
        plt.scatter(range(1, 11), mapp)
        plt.show()

    else:
        print("Invalid option selected.")

# Driver code
if __name__ == '__main__':
    main()
