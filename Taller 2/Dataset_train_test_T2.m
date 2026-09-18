%% Dataset_train_test_T2: división de Wine y Breast Cancer Wisconsin en entrenamiento y prueba
% Versión análoga al script Dataset_train_test del Taller 1, para los dos
% conjuntos del numeral 5. Mezcla con semilla fija y corta en 60-40, 70-30,
% 80-20 y 90-10. Deja las particiones en la estructura |S| y muestra los
% tamaños y el reparto de clases de cada una.
clear; close all; clc

archivos = {'wine.data', 'wdbc.data'};
nombres  = {'Wine', 'Breast Cancer Wisconsin'};
proporciones = [0.6 0.7 0.8 0.9];

for d = 1:2
    [X, y] = leer_conjunto(archivos{d});
    No_examples = size(X, 1);
    rng(2021)
    ind = randperm(No_examples);
    fprintf('\n%s, %d ejemplos, %d atributos, %d clases\n', nombres{d}, No_examples, size(X, 2), numel(unique(y)));
    for k = 1:4
        n_train = round(proporciones(k) * No_examples);
        S(d, k).p   = proporciones(k);
        S(d, k).Xtr = X(ind(1:n_train), :);
        S(d, k).ytr = y(ind(1:n_train));
        S(d, k).Xte = X(ind(n_train+1:end), :);
        S(d, k).yte = y(ind(n_train+1:end));
        fprintf('  %2.0f-%2.0f  entrenamiento %3d  prueba %3d  clases en prueba %s\n', ...
            100*proporciones(k), 100*(1-proporciones(k)), n_train, No_examples - n_train, mat2str(histcounts(S(d, k).yte)));
    end
end
S

%% Ejemplo: la partición 60-40 de Wine con la clase en la última columna, como en el original
wine_train60 = [S(1, 1).Xtr S(1, 1).ytr];
wine_test40 = S(1, 1).Xte;
wine_testclass40 = S(1, 1).yte;
size(wine_train60), size(wine_test40)

function [X, y] = leer_conjunto(archivo)
    % Wine trae la clase en la primera columna. Breast Cancer trae un identificador,
    % luego la etiqueta M o B y después los 30 atributos.
    switch archivo
        case 'wine.data'
            M = readmatrix(archivo, 'FileType', 'text');
            X = M(:, 2:end);  y = M(:, 1);
        case 'wdbc.data'
            T = readtable(archivo, 'FileType', 'text', 'ReadVariableNames', false);
            X = table2array(T(:, 3:end));  y = double(strcmp(T{:, 2}, 'M'));
    end
end
