%% Dataset_train_test_T2: división de Wine y Breast Cancer Wisconsin en entrenamiento y prueba
% Versión análoga al script Dataset_train_test del Taller 1, para los dos
% conjuntos del numeral 5. Mezcla con semilla fija y corta en 60-40, 70-30,
% 80-20 y 90-10. Deja las particiones en la estructura |S| y muestra los
% tamaños y los patrones de prueba por clase. Usa la misma semilla que el live
% script principal, así que los cortes son los evaluados allí.
clear; close all; clc

semilla = 1;                      % la misma de cfg.seed en el live script
archivos = {'wine.data', 'wdbc.data'};
nombres  = {'Wine', 'Breast Cancer Wisconsin'};
proporciones = [0.6 0.7 0.8 0.9];

for d = 1:numel(archivos)
    [X, y] = leer_conjunto(archivos{d});
    No_examples = size(X, 1);
    clases = unique(y);
    rng(semilla)
    ind = randperm(No_examples);
    fprintf('\n%s, %d ejemplos, %d atributos, %d clases\n', nombres{d}, No_examples, size(X, 2), numel(clases));
    for k = 1:numel(proporciones)
        n_train = round(proporciones(k) * No_examples);
        S(d, k).p   = proporciones(k);
        S(d, k).Xtr = X(ind(1:n_train), :);
        S(d, k).ytr = y(ind(1:n_train));
        S(d, k).Xte = X(ind(n_train+1:end), :);
        S(d, k).yte = y(ind(n_train+1:end));
        por_clase = arrayfun(@(c) sum(S(d, k).yte == c), clases)';
        fprintf('  %2.0f-%2.0f  entrenamiento %3d  prueba %3d  patrones de prueba por clase %s\n', ...
            100*proporciones(k), 100*(1-proporciones(k)), n_train, No_examples - n_train, mat2str(por_clase));
    end
end

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
        otherwise
            error('Archivo desconocido: %s', archivo);
    end
end
