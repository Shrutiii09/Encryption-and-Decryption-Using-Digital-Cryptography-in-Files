from django.shortcuts import render,HttpResponse
from PIL import Image
import io

def home(request):
    return render(request, 'home.html')

def encrypt(request):
    if request.method == 'POST' and request.FILES['file'] and request.POST['message']:
        image_file = request.FILES['file']
        message = request.POST['message']
     
        image = Image.open(image_file)
        encoded_image = encode_message_in_image(image, message)

        #Save encoded image
        byte_stream = io.BytesIO()
        encoded_image.save(byte_stream, format='PNG')
        byte_stream.seek(0)

        #Return modified image
        response = HttpResponse(byte_stream, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="encoded_image.png"'
        return response

    return render(request, 'encrypt.html')

def decrypt(request):
    if request.method == 'POST' and request.FILES['file']:
        image_file = request.FILES['file']

        image = Image.open(image_file)
        hidden_message = decode_message_from_image(image)

        return render(request, 'decrypt.html', {'message': hidden_message})

    return render(request, 'decrypt.html')


def encode_message_in_image(image, message):
    encoded = image.copy()
    width, height = image.size
    message += '###'  

    # Convert message to binary
    binary_message = ''.join([format(ord(char), '08b') for char in message])
    
    #image has enough space to hold the message
    if len(binary_message) > width * height * 3:
        raise ValueError("Message is too large for the image.")

    binary_index = 0
    pixels = list(encoded.getdata())

    for i in range(len(pixels)):
        pixel = list(pixels[i])

        for j in range(3):  # Loop through RGB channels
            if binary_index < len(binary_message):
                pixel[j] = pixel[j] & ~1 | int(binary_message[binary_index])
                binary_index += 1

        pixels[i] = tuple(pixel)

    encoded.putdata(pixels)
    return encoded

def decode_message_from_image(image):
    binary_message = ''
    pixels = list(image.getdata())

    for pixel in pixels:
        for color_value in pixel[:3]:  
            binary_message += str(color_value & 1)

    # Convert binary message back to a string
    message = ''.join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)])

    end_index = message.find('###')
    if end_index != -1:
        return message[:end_index]
    else:
        return "No hidden message found."
    
def learn(request):
    return render(request, 'learn.html')

