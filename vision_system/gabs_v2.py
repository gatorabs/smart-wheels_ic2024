import cv2
import numpy as np
import time


def nothing(x):
    pass

num_cameras = 1
frame_width, frame_height = 480, 270
desired_fps = 60  # FPS desejado
frame_time = 1 / desired_fps  # Tempo de cada frame

cap1 = cv2.VideoCapture(0)
if num_cameras == 2:
    cap2 = cv2.VideoCapture(1)

cap1.set(cv2.CAP_PROP_FPS, 60)
if num_cameras == 2:
    cap2.set(cv2.CAP_PROP_FPS, 60)


cv2.namedWindow("Trackbars")


cv2.createTrackbar("L - H", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 200, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - S", "Trackbars", 50, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

# Trackbar para selecionar a direção: 0 para direita, 1 para esquerda
cv2.createTrackbar("Direção (0: direita, 1: esquerda)", "Trackbars", 0, 1, nothing)


prev_time = time.time()
show_video = False

while True:
    start_time = time.time()

    success1, frame1 = cap1.read()
    if not success1:
        print("Failed to capture from camera.")
        break

    frame = cv2.resize(frame1, (frame_width, frame_height))

    # Definição dos pontos para transformar a perspectiva
    tl = (0, int(frame_height * 0.875))
    bl = (0, frame_height)
    tr = (frame_width, int(frame_height * 0.875))
    br = (frame_width, frame_height)

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
    cv2.line(mask, (central_x, 0), (central_x, frame_height), (255, 255, 255), 2)

    points = [(central_x, y) for y in range(0, frame_height, 20)]
    for point_position in points:
        cv2.circle(mask, point_position, 3, (0, 255, 0), -1)

    direcao = cv2.getTrackbarPos("Direção (0: direita, 1: esquerda)", "Trackbars")
    distancias = []

    for point in points:
        x, y = point
        found_white = False
        start_x = x

        if direcao == 0:  # Analisar à direita
            while x < frame_width:
                if mask[y, x] == 255:  # White pixel found
                    found_white = True
                    distance = x - central_x
                    distancias.append(distance)
                    #print(f"White pixel found at row {y}, column {x} (right side), distance: {distance}")
                    #cv2.line(transformed_frame, (start_x, y), (x, y), (0, 255, 0), 2)
                    break
                x += 1
        else:  # Analisar à esquerda
            while x > 0:
                if mask[y, x] == 255:  # White pixel found
                    found_white = True
                    distance = central_x - x
                    distancias.append(distance)
                    #print(f"White pixel found at row {y}, column {x} (left side), distance: {distance}")
                    #cv2.line(transformed_frame, (start_x, y), (x, y), (0, 255, 0), 2)  # Draw a green line
                    break
                x -= 1

        if not found_white:
            print(f"No white pixel found at row {y}.")


    if distancias:
        media_distancia = sum(distancias) / len(distancias)
        print(f"Média das distâncias: {media_distancia:.2f}")

        if 180 <= media_distancia <= 240:
            print("Carrinho deve seguir reto.")
        else:
            min_distancia = 20
            max_distancia = 240
            min_angle = 60
            max_angle = 140

            media_distancia = np.clip(media_distancia, min_distancia, max_distancia)
            angle = int(
                ((media_distancia - min_distancia) / (max_distancia - min_distancia)) * (max_angle - min_angle) + min_angle
            )
            print(f"Ângulo do servo motor: {angle} graus")
    else:
        print("Nenhuma distância válida encontrada.")

    # Medindo FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    print(f"FPS: {int(fps)}")


    if show_video:
        cv2.imshow("Original", frame)
        cv2.imshow("Bird's Eye View", transformed_frame)
        cv2.imshow("Lane Detection - Image Thresholding", mask)


    elapsed_time = time.time() - start_time
    if elapsed_time < frame_time:
        time.sleep(frame_time - elapsed_time)


    key = cv2.waitKey(1) & 0xFF


    if key == 27:  # Pressione 'ESC' para sair
        break

cap1.release()
cv2.destroyAllWindows()
