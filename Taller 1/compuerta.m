function [X, d] = compuerta(tipo, n, salida)
% COMPUERTA  Tabla de verdad de una compuerta AND, OR o XOR de n entradas.
% Las entradas van en {0,1}. La salida se codifica con salida = [min max],
% por ejemplo [-1 1] o [0 1].
%
% X : 2^n x n, todas las combinaciones de entrada
% d : 2^n x 1, salida deseada

if nargin < 3, salida = [-1 1]; end

X = zeros(2^n, n);
for k = 1:2^n
    X(k, :) = bitget(k - 1, n:-1:1);   % k-1 en binario, n bits
end

switch upper(tipo)
    case 'AND', logico = all(X, 2);
    case 'OR',  logico = any(X, 2);
    case 'XOR', logico = mod(sum(X, 2), 2) == 1;
    otherwise,  error('compuerta desconocida: %s', tipo);
end

d = salida(1) * ones(2^n, 1);
d(logico) = salida(2);
end
