function [w, b, info] = perceptron(X, d, op)
% PERCEPTRON  Red de una sola neurona y una sola capa (perceptron simple).
%
% Se puede escoger la regla de correccion de pesos con op.regla:
%   1 -> dW = d(x) * X
%   2 -> dW = [d(x) - Y(x)] * X
%   3 -> dW = alpha * [d(x) - Y(x)] * X
% y el ajuste siempre es W = W + dW. El bias se maneja como el peso w0 de
% una entrada constante igual a 1, como en la figura del taller.
%
% X : matriz N x n, una fila por patron y una columna por entrada
% d : vector N x 1 con la salida deseada de cada patron
% op: estructura con los parametros del modelo (todos opcionales)
%       op.regla       1, 2 o 3                          (por defecto 3)
%       op.alpha       factor relativo de aprendizaje    (0.1)
%       op.umbral      umbral de la funcion escalon      (0)
%       op.salida      [min max] con que se codifica la salida ([-1 1])
%       op.max_epocas  tope de epocas si no converge     (100)
%       op.semilla     semilla de los pesos iniciales    (1)
%
% w, b : pesos y bias finales
% info : epocas, convergio, errores_por_epoca, w_ini, b_ini

if nargin < 3, op = struct(); end
if ~isfield(op, 'regla'),      op.regla = 3;        end
if ~isfield(op, 'alpha'),      op.alpha = 0.1;      end
if ~isfield(op, 'umbral'),     op.umbral = 0;       end
if ~isfield(op, 'salida'),     op.salida = [-1 1];  end
if ~isfield(op, 'max_epocas'), op.max_epocas = 100; end
if ~isfield(op, 'semilla'),    op.semilla = 1;      end

[N, n] = size(X);
d = d(:);

% pesos iniciales aleatorios entre 0 y 1
rng(op.semilla);
w = rand(1, n);
b = rand;
info.w_ini = w;
info.b_ini = b;

errores = zeros(op.max_epocas, 1);
epocas = 0;
convergio = false;

% una epoca = pasar por todos los patrones una vez. Se para cuando en una
% epoca completa no hubo que corregir ningun peso (equivale al aux<4 del
% codigo de clase) o cuando se llega al tope de epocas.
while epocas < op.max_epocas && ~convergio
    epocas = epocas + 1;
    n_err = 0;
    for i = 1:N
        x = X(i, :);
        z = sum(w .* x) + b;          % suma ponderada
        if z > op.umbral              % funcion de activacion escalon
            y = op.salida(2);
        else
            y = op.salida(1);
        end
        e = d(i) - y;
        if e ~= 0
            switch op.regla
                case 1
                    dw = d(i) * x;          db = d(i);
                case 2
                    dw = e * x;             db = e;
                case 3
                    dw = op.alpha * e * x;  db = op.alpha * e;
            end
            w = w + dw;
            b = b + db;
            n_err = n_err + 1;
        end
    end
    errores(epocas) = n_err;
    convergio = (n_err == 0);
end

info.epocas = epocas;
info.convergio = convergio;
info.errores_por_epoca = errores(1:epocas);
end
