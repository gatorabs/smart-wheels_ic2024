import cv2
import numpy as np

import serial
import time

#ser = serial.Serial('COM3', 9600)



def nothing(x):
    pass


num_cameras = 1
frame_width, frame_height = 480, 270

cap1 = cv2.VideoCapture(0)
if num_cameras == 2:
    cap2 = cv2.VideoCapture(1)

cv2.namedWindow("Trackbars")

# Trackbars para ajuste de HSV
cv2.createTrackbar("L - H", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 200, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - S", "Trackbars", 50, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

# Trackbar para selecionar a direção: 0 para direita, 1 para esquerda
cv2.createTrackbar("Direção (0: direita, 1: esquerda)", "Trackbars", 0, 1, nothing)

while True:
    success1, frame1 = cap1.read()

    if num_cameras == 2:
        success2, frame2 = cap2.read()
        if not success2:
            print("Failed to capture from second camera.")
            break

        frame1 = cv2.resize(frame1, (frame_width // 2, frame_height))
        frame2 = cv2.resize(frame2, (frame_width // 2, frame_height))

        frame = np.hstack((frame1, frame2))
    else:
        if not success1:
            print("Failed to capture from camera.")
            break

        frame = cv2.resize(frame1, (frame_width, frame_height))

    tl = (0, int(frame_height * 0.875))  # 420/480 = 0.875
    bl = (0, frame_height)
    tr = (frame_width, int(frame_height * 0.875))  # 420/480 = 0.875
    br = (frame_width, frame_height)

    cv2.circle(frame, tl, 5, (0, 0, 255), -1)
    cv2.circle(frame, bl, 5, (0, 0, 255), -1)
    cv2.circle(frame, tr, 5, (0, 0, 255), -1)
    cv2.circle(frame, br, 5, (0, 0, 255), -1)

    pts1 = np.float32([tl, bl, tr, br])
    pts2 = np.float32([[0, 0], [0, frame_height], [frame_width, 0], [frame_width, frame_height]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    transformed_frame = cv2.warpPerspective(frame, matrix, (frame_width, frame_height))

    hsv_transformed_frame = cv2.cvtColor(transformed_frame, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower = np.array([l_h, l_s, l_v])
    upper = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv_transformed_frame, lower, upper)

    central_x = frame_width // 2
    # Drawing the vertical line
    cv2.line(mask, (central_x, 0), (central_x, frame_height), (255, 255, 255), 2)
    cv2.line(transformed_frame, (central_x, 0), (central_x, frame_height), (255, 255, 255), 2)

    points = []  # List to store point positions
    for y in range(0, frame_height, 20):  # Adjust step as needed
        point_position = (central_x, y)
        points.append(point_position)  # Add position to the list
        cv2.circle(mask, point_position, 3, (0, 255, 0), -1)  # Adding point at (central_x, y)

    # Pegar valor da trackbar de direção (0 para direita, 1 para esquerda)
    direcao = cv2.getTrackbarPos("Direção (0: direita, 1: esquerda)", "Trackbars")

    # Lista para armazenar distâncias encontradas
    distancias = []

    for point in points:
        x, y = point
        found_white = False
        start_x = x

        if direcao == 0:  # Analisar à direita
            while x < frame_width:
                if mask[y, x] == 255:  # White pixel found
                    found_white = True
                    distance = x - central_x  # Calcular a distância
                    distancias.append(distance)  # Armazenar distância
                    print(f"White pixel found at row {y}, column {x} (right side), distance: {distance}")
                    cv2.line(transformed_frame, (start_x, y), (x, y), (0, 255, 0), 2)  # Draw a green line
                    break
                x += 1
        else:  # Analisar à esquerda
            while x > 0:
                if mask[y, x] == 255:  # White pixel found
                    found_white = True
                    distance = central_x - x  # Calcular a distância
                    distancias.append(distance)  # Armazenar distância
                    print(f"White pixel found at row {y}, column {x} (left side), distance: {distance}")
                    cv2.line(transformed_frame, (start_x, y), (x, y), (0, 255, 0), 2)  # Draw a green line
                    break
                x -= 1

        if not found_white:
            print(f"No white pixel found at row {y}.")

    # Calcular e exibir a média das distâncias, se houver distâncias
    if distancias:
        media_distancia = sum(distancias) / len(distancias)
        print(f"Média das distâncias: {media_distancia:.2f}")
        if 180 <= media_distancia <= 240:
            print("Carrinho deve seguir reto.")
            #ser.write(f"{angle}\n".encode())
        else:
            # Caso contrário, ajusta o ângulo do servo motor com base na distância média
            min_distancia = 20  # Distância mínima esperada
            max_distancia = 240  # Distância máxima esperada
            min_angle = 60  # Ângulo mínimo do servo
            max_angle = 140  # Ângulo máximo do servo

            if media_distancia < min_distancia:
                media_distancia = min_distancia
            elif media_distancia > max_distancia:
                media_distancia = max_distancia

            angle = int(
                ((media_distancia - min_distancia) / (max_distancia - min_distancia)) * (
                            max_angle - min_angle) + min_angle)

            print(f"Ângulo do servo motor: {angle} graus")
            #ser.write(f"{angle}\n".encode())  # Envia o ângulo calculado via serial
        min_distancia = 20  # Distância mínima esperada
        max_distancia = 240   # Distância máxima esperada
        min_angle = 60        # Ângulo mínimo do servo
        max_angle = 140       # Ângulo máximo do servo

        if media_distancia < min_distancia:
            media_distancia = min_distancia
        elif media_distancia > max_distancia:
            media_distancia = max_distancia
        angle = int(
            ((media_distancia - min_distancia) / (max_distancia - min_distancia)) * (max_angle - min_angle) + min_angle)
        print(f"Ângulo do servo motor: {angle} graus")
        #ser.write(f"{angle}\n".encode())
    else:
        print("Nenhuma distância válida encontrada.")

    cv2.imshow("Original", frame)
    cv2.imshow("Bird's Eye View", transformed_frame)
    cv2.imshow("Lane Detection - Image Thresholding", mask)

    if cv2.waitKey(10) == 27:
        break

cap1.release()
if num_cameras == 2:
    cap2.release()
cv2.destroyAllWindows()
#ser.close()