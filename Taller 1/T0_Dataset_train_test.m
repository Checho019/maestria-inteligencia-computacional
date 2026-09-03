%% Dataset_train_test: division de Iris en entrenamiento y test
% Es el script del profe, con dos cambios: el corte se hace con round para
% que sirva con cualquier tamano de dataset, y las cuatro particiones se
% guardan en un .mat para que los otros scripts las carguen tal cual.
clear; close all; clc

load iris.dat
No_examples = length(iris);
fprintf('Iris: %d ejemplos, %d columnas (4 atributos + clase)\n', size(iris, 1), size(iris, 2));

%% Se mezcla el dataset con una semilla fija
% Asi la muestra queda aleatoria pero se puede repetir.
rng(2021)
ind = randperm(No_examples);

%% Division 60-40, 70-30, 80-20 y 90-10
% Se usa el mismo orden mezclado y solo cambia el punto de corte, igual que
% en el script original.
proporciones = [0.6 0.7 0.8 0.9];
S = struct([]);
for k = 1:numel(proporciones)
    p = proporciones(k);
    n_train = round(p * No_examples);

    S(k).p    = p;
    S(k).Xtr  = iris(ind(1:n_train), 1:4);
    S(k).ytr  = iris(ind(1:n_train), 5);
    S(k).Xte  = iris(ind(n_train+1:end), 1:4);
    S(k).yte  = iris(ind(n_train+1:end), 5);

    fprintf('%d-%d : %3d de entrenamiento, %3d de test | clases en train: %s\n', ...
        round(100*p), round(100*(1-p)), n_train, No_examples - n_train, ...
        mat2str(histcounts(S(k).ytr, 1:4)));
end

%% Ejemplo: la particion 60-40 tal como la deja el script original
iris_train60 = [S(1).Xtr S(1).ytr];
iris_test40  = S(1).Xte;
iris_testclass40 = S(1).yte;
disp(size(iris_train60)); disp(size(iris_test40)); disp(size(iris_testclass40));

%% Se guardan las particiones
save('iris_splits.mat', 'S');
disp('Particiones guardadas en iris_splits.mat')
