function y = predecir(X, w, b, umbral, salida)
% PREDECIR  Salida de la neurona ya entrenada: suma ponderada y escalon.
% Sirve igual para el perceptron y para el Adaline, porque en los dos la
% clasificacion final es "si la suma pasa el umbral, salida max; si no, min".
z = X * w(:) + b;
y = salida(1) * ones(size(z));
y(z > umbral) = salida(2);
end
