function y = predecir(X, w, b, umbral, salida)
% Suma ponderada y escalon. Sirve para el perceptron y para el Adaline.
z = X * w(:) + b;
y = salida(1) * ones(size(z));
y(z > umbral) = salida(2);
end
