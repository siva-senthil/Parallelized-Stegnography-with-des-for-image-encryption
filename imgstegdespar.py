import os
import time
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

class Steganography:
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

def get_absolute_path(relative_path):
    base_dir = os.path.abspath(os.getcwd())
    return os.path.join(base_dir, relative_path)

def process_merge(img1_path, img2_path, output_path, encrypted_path, key):
    try:
        print(f"Processing merge for {img1_path} and {img2_path}")
        encrypted_img2 = Steganography.encrypt_image(img2_path, key)
        with open(encrypted_path, 'wb') as enc_file:
            enc_file.write(encrypted_img2)
        merged_img = Steganography.merge(Image.open(img1_path), Image.open(img2_path))
        merged_img.save(output_path)
        print(f"Saved merged image to {output_path}")
    except Exception as e:
        print(f"Error during merge: {e}")

def process_unmerge(img_path, encrypted_path, decrypted_path, output_path, key):
    try:
        print(f"Processing unmerge for {img_path}")
        with open(encrypted_path, 'rb') as enc_file:
            encrypted_data = enc_file.read()
        decrypted_data = Steganography.decrypt_image(encrypted_data, key)
        with open(decrypted_path, 'wb') as dec_file:
            dec_file.write(decrypted_data)
        unmerged_image = Steganography.unmerge(img_path)
        unmerged_image.save(output_path)
        print(f"Saved unmerged image to {output_path}")
    except Exception as e:
        print(f"Error during unmerge: {e}")

def main():
    choice = int(input(":: Welcome to Steganography ::\n1. Encrypt and Merge\n2. Unmerge and Decrypt\n"))
    key = b'12345678'  # DES key

    # Define directories
    resultoutpar = get_absolute_path('resultoutpar')
    encrypted_dir = get_absolute_path('encrypted')
    decrypted_dir = get_absolute_path('decrypted')
    decodepar = get_absolute_path('decodepar')

    # Ensure output directories exist
    os.makedirs(resultoutpar, exist_ok=True)
    os.makedirs(encrypted_dir, exist_ok=True)
    os.makedirs(decrypted_dir, exist_ok=True)
    os.makedirs(decodepar, exist_ok=True)

    with ThreadPoolExecutor(max_workers=4) as executor:
        if choice == 1:
            time_records = []
            for i in range(10):
                img1_path = get_absolute_path(f'big/b{i}.png')
                img2_path = get_absolute_path(f'small/s{i}.png')
                output_path = os.path.join(resultoutpar, f'rr{i}.png')
                encrypted_path = os.path.join(encrypted_dir, f'encrypted_s{i}.bin')

                # Check if the images exist
                if not os.path.exists(img1_path) or not os.path.exists(img2_path):
                    print(f"Error: Image files {img1_path} or {img2_path} not found!")
                    continue

                print(f"Submitting merge task for image {i}...")
                start_time = time.time()
                executor.submit(process_merge, img1_path, img2_path, output_path, encrypted_path, key)
                end_time = time.time()
                time_records.append(end_time - start_time)

            plot_path = get_absolute_path("encoding_time.png")
            plt.xlabel('Number of images')
            plt.ylabel('Parallel Time (seconds)')
            plt.title(f"Time to encode 10 images in parallel: {sum(time_records)}")
            plt.scatter(range(1, 11), time_records)
            plt.savefig(plot_path)
            print(f"Encoding time plot saved at {plot_path}")

        elif choice == 2:
            time_records = []
            for i in range(10):
                img3_path = os.path.join(resultoutpar, f'rr{i}.png')
                encrypted_path = os.path.join(encrypted_dir, f'encrypted_s{i}.bin')
                decrypted_path = os.path.join(decrypted_dir, f'decrypted_s{i}.png')
                output_path = os.path.join(decodepar, f'dd{i}.png')

                # Check if the images exist
                if not os.path.exists(img3_path) or not os.path.exists(encrypted_path):
                    print(f"Error: Image files {img3_path} or {encrypted_path} not found!")
                    continue

                print(f"Submitting unmerge task for image {i}...")
                start_time = time.time()
                executor.submit(process_unmerge, img3_path, encrypted_path, decrypted_path, output_path, key)
                end_time = time.time()
                time_records.append(end_time - start_time)

            plot_path = get_absolute_path("decoding_time.png")
            plt.xlabel('Number of images')
            plt.ylabel('Parallel Time (seconds)')
            plt.title(f"Time to decode 10 images in parallel: {sum(time_records)}")
            plt.scatter(range(1, 11), time_records)
            plt.savefig(plot_path)
            print(f"Decoding time plot saved at {plot_path}")

        else:
            print("Invalid option selected.")

if __name__ == '__main__':
    main()
