function [w, b, epocas, EC_hist] = adaline(X, d, alpha, error_min, max_epocas, semilla, tol_cambio)
% Adaline de una neurona con regla delta: dW = alpha*(d - y)*x, con y la salida lineal.
% Para cuando EC = 1/2*sum(e^2) baja de error_min o cuando deja de cambiar (tol_cambio).

if nargin < 7, tol_cambio = 1e-6; end
rng(semilla);
w = rand(1, size(X, 2));
b = rand;

epocas = 0;
EC = Inf;
EC_hist = [];
seguir = true;
while epocas < max_epocas && seguir
    epocas = epocas + 1;
    e = zeros(size(X, 1), 1);
    for i = 1:size(X, 1)
        y = sum(w .* X(i, :)) + b;
        e(i) = d(i) - y;
        w = w + alpha * e(i) * X(i, :);
        b = b + alpha * e(i);
    end
    EC_ant = EC;
    EC = 0.5 * sum(e .^ 2);
    EC_hist(epocas) = EC;
    if ~isfinite(EC), break, end
    seguir = EC > error_min && abs(EC_ant - EC) > tol_cambio;
end
end
