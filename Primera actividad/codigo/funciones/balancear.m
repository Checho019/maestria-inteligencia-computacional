function [Xb, yb] = balancear(X, y, metodo)
% Balancea las clases hasta dejarlas todas del mismo tamano.
%
%   metodo = 'smote'        -> sobremuestreo sintetico hasta el tamano de la
%                              clase mayoritaria. Se usa cuando n es chico y
%                              tirar datos duele.
%   metodo = 'submuestreo'  -> se recorta la clase mayoritaria al tamano de
%                              la minoritaria. Se usa cuando n es grande.
%   metodo = 'sobremuestreo'-> replica con reemplazo (sin sintetizar).

clases = categories(removecats(categorical(y)));
conteo = zeros(numel(clases), 1);
for i = 1:numel(clases)
    conteo(i) = sum(strcmp(cellstr(y), clases{i}));
end

switch metodo
    case 'submuestreo'
        objetivo = min(conteo);
    otherwise
        objetivo = max(conteo);
end

Xb = []; yb = {};
for i = 1:numel(clases)
    filas = find(strcmp(cellstr(y), clases{i}));
    Xi = X(filas, :);
    ni = numel(filas);

    if ni > objetivo                       % sobran -> se recorta al azar
        sel = randperm(ni, objetivo);
        Xi = Xi(sel, :);
    elseif ni < objetivo                   % faltan -> se generan
        faltan = objetivo - ni;
        if strcmp(metodo, 'smote')
            Xi = [Xi; smote_simple(Xi, faltan, 5)];   %#ok<AGROW>
        else
            Xi = [Xi; Xi(randi(ni, faltan, 1), :)];   %#ok<AGROW>
        end
    end

    Xb = [Xb; Xi];                                     %#ok<AGROW>
    yb = [yb; repmat(clases(i), size(Xi,1), 1)];       %#ok<AGROW>
end

% se revuelve para que no queden las clases en bloques
orden = randperm(size(Xb,1));
Xb = Xb(orden, :);
yb = yb(orden);
end
