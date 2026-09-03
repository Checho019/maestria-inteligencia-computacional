function [w, b, info] = adaline(X, d, op)
% ADALINE  Red de una sola neurona con activacion lineal (regla delta).
%
% La correccion de pesos se hace de una unica forma:
%   dW = alpha * [d(x) - Y(x)] * X
% pero aqui Y(x) es la salida LINEAL de la neurona (la suma ponderada),
% no la salida del escalon. Esa es la diferencia con el perceptron. El
% escalon solo se usa despues, para clasificar (ver predecir.m).
%
% X : matriz N x n, una fila por patron
% d : vector N x 1 con la salida deseada
% op: estructura con los parametros (todos opcionales)
%       op.alpha       factor relativo de aprendizaje         (0.01)
%       op.umbral      umbral del escalon al clasificar       (0.5)
%       op.salida      [min max] de la salida                 ([0 1])
%       op.error_min   se para cuando EC baja de este valor   (1e-3)
%       op.tol_cambio  o cuando EC ya casi no cambia entre
%                      una epoca y la siguiente               (1e-6)
%       op.max_epocas  tope de epocas                         (1000)
%       op.semilla     semilla de los pesos iniciales         (1)
%
% Hacen falta los dos criterios: con una tabla de verdad la salida lineal
% nunca calza exacto con los 0 y 1 deseados, asi que el EC se estanca en
% un valor distinto de cero y con solo error_min nunca pararia.
%
% w, b : pesos y bias finales
% info : epocas, convergio, ec_por_epoca (EC = 1/2*sum(e^2)), w_ini, b_ini

if nargin < 3, op = struct(); end
if ~isfield(op, 'alpha'),      op.alpha = 0.01;      end
if ~isfield(op, 'umbral'),     op.umbral = 0.5;      end
if ~isfield(op, 'salida'),     op.salida = [0 1];    end
if ~isfield(op, 'error_min'),  op.error_min = 1e-3;  end
if ~isfield(op, 'tol_cambio'), op.tol_cambio = 1e-6; end
if ~isfield(op, 'max_epocas'), op.max_epocas = 1000; end
if ~isfield(op, 'semilla'),    op.semilla = 1;       end

[N, n] = size(X);
d = d(:);

rng(op.semilla);
w = rand(1, n);
b = rand;
info.w_ini = w;
info.b_ini = b;

ec = zeros(op.max_epocas, 1);
epocas = 0;
EC = Inf;
seguir = true;

% mismo esquema del codigo_Adaline de clase: se recorre patron por patron
% corrigiendo, y al final de la epoca se calcula el error cuadratico
while epocas < op.max_epocas && seguir
    epocas = epocas + 1;
    e = zeros(N, 1);
    for i = 1:N
        x = X(i, :);
        y = sum(w .* x) + b;          % salida lineal (identidad)
        e(i) = d(i) - y;
        w = w + op.alpha * e(i) * x;  % regla delta
        b = b + op.alpha * e(i);
    end
    EC_ant = EC;
    EC = 0.5 * sum(e .^ 2);
    ec(epocas) = EC;
    if ~isfinite(EC)                  % con alpha grande el error se dispara
        break
    end
    % se para si el error ya es chico o si dejo de bajar
    seguir = EC > op.error_min && abs(EC_ant - EC) > op.tol_cambio;
end

info.epocas = epocas;
info.convergio = isfinite(EC) && ~seguir;   % paro por alguno de los dos criterios
info.ec_por_epoca = ec(1:epocas);
info.ec_final = EC;
end
