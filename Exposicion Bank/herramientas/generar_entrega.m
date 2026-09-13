function generar_entrega
% Genera el mlx ejecutado de la carpeta entrega. Se llama desde la carpeta Exposicion Bank.
cd entrega
mlx = fullfile(pwd, 'procesar_bank.mlx');
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'procesar_bank.m'), mlx);
matlab.internal.liveeditor.executeAndSave(mlx);
close all
delete('procesar_bank.m')
cd ..
end
