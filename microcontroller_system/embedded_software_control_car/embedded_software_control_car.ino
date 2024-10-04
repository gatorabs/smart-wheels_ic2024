#include <Servo.h>


int velocidade = 0;
int direcao = 0;  
String dadoRecebido = "";
bool dadoCompleto = false;


#define IN1 25
#define IN2 26
#define IN3 19
#define IN4 21

#define ENA_A 2
#define ENA_B 4
#define servoPin 6

Servo servo_direcao;

// Tempo de controle
unsigned long tempoUltimoProcessamento = 0;
const unsigned long intervaloProcessamento = 100; 

void setup() {
  
  Serial.begin(115200);
  
  
  servo_direcao.attach(servoPin);

 
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.println("Aguardando dados...");
}

void loop() {
  
  while (Serial.available()) {
    char caractere = Serial.read();
    dadoRecebido += caractere;
    if (caractere == '#') {
      dadoCompleto = true;  // Finaliza a recepção ao encontrar o '#'
    }
  }

  
  if (dadoCompleto && (millis() - tempoUltimoProcessamento >= intervaloProcessamento)) {
   
    tempoUltimoProcessamento = millis();

    
    digitalWrite(LED_BUILTIN, HIGH);
    

    // Processa os dados recebidos
    int dados[8];
    int index = 0;
    String temp = "";
    
    for (int i = 0; i < dadoRecebido.length(); i++) {
      if (dadoRecebido[i] == ',') {
        dados[index] = temp.toInt();
        temp = "";
        index++;
      }
    }

    if (index >= 1) {

      velocidade = dados[0];  // A velocidade é recebida em RPM
      direcao = dados[1];

      Serial.print("Velocidade: ");
      Serial.println(velocidade);
      Serial.print("Direção: ");
      Serial.println(direcao);

      servo_direcao.write(direcao);  

      
      if (velocidade > 0) {

        
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENA_A, velocidade);  // Define a velocidade do Motor A
        analogWrite(ENA_B, velocidade);  // Define a velocidade do Motor B
      } else {
        
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, LOW);
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, LOW);
      }
    }

    // Limpa as variáveis para a próxima leitura
    dadoRecebido = "";
    dadoCompleto = false;
    digitalWrite(LED_BUILTIN, LOW);
  } else if (!dadoCompleto) {
    Serial.println("Aguardando dados...");
  }
}
