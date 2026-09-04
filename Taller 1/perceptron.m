function [w, b, epocas, convergio] = perceptron(X, d, regla, alpha, umbral, salida, max_epocas, semilla)
% Perceptron simple de una neurona.
% regla 1: dW = d*x     regla 2: dW = (d-y)*x     regla 3: dW = alpha*(d-y)*x
% X: patrones por filas, d: salida deseada, salida = [min max]

rng(semilla);
w = rand(1, size(X, 2));
b = rand;

epocas = 0;
aux = 0;
while epocas < max_epocas && aux < size(X, 1)
    epocas = epocas + 1;
    aux = 0;
    for i = 1:size(X, 1)
        z = sum(w .* X(i, :)) + b;
        if z > umbral
            y = salida(2);
        else
            y = salida(1);
        end
        error = d(i) - y;
        if error ~= 0
            switch regla
                case 1, dw = d(i) * X(i, :);         db = d(i);
                case 2, dw = error * X(i, :);        db = error;
                case 3, dw = alpha * error * X(i, :); db = alpha * error;
            end
            w = w + dw;
            b = b + db;
        else
            aux = aux + 1;
        end
    end
end
convergio = aux == size(X, 1);
end
