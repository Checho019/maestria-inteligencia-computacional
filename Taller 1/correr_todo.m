function correr_todo
% Corre los ocho scripts del taller en orden. Cada uno empieza con clear,
% por eso se llaman desde una funcion: asi el clear no borra el listado.
scripts = {'T0_Dataset_train_test', 'T1_perceptron_compuertas', 'T2_perceptron_iris', ...
           'T3_dataset_banknote', 'T4_perceptron_banknote', 'T5_adaline_compuertas', ...
           'T6_adaline_iris', 'T7_adaline_banknote'};
for k = 1:numel(scripts)
    fprintf('\n######## %s ########\n', scripts{k});
    t = tic;
    try
        correr(scripts{k});
        fprintf('>>> OK %s en %.1f s\n', scripts{k}, toc(t));
    catch e
        fprintf('>>> ERROR en %s: %s\n', scripts{k}, e.message);
        for j = 1:numel(e.stack)
            fprintf('    %s linea %d\n', e.stack(j).name, e.stack(j).line);
        end
    end
    close all
end
end

function correr(nombre)
run(nombre);
end
