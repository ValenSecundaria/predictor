'use client';

import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from 'react';
import {
  ChakraProvider,
  Container,
  Heading,
  Button,
  Box,
  SimpleGrid,
  Text,
} from '@chakra-ui/react';
import Link from 'next/link';

export default function Page() {
  const [mode, setMode] = useState<'usuario' | null>(null);

  return (
    <ChakraProvider>
      <Container maxW="container.md" className="pt-4">
        {mode === null && (
          <Box textAlign="center" py={10} px={6}>
            <Heading as="h2" size="xl" mt={6} mb={2}>
              Bienvenido al Predictor Mundial
            </Heading>
            <Text mb={4}>Selecciona un modo para continuar</Text>

            <Button colorScheme="teal" onClick={() => setMode('usuario')} mr={3}>
              Modo Usuario
            </Button>

            <Link href="/pruebas">
              <Button colorScheme="blue">
                Modo pruebas
              </Button>
            </Link>
          </Box>
        )}

        {mode === 'usuario' && (
          <Box textAlign="center" py={10} px={6}>
            <Heading as="h2" size="lg" mb={6}>
              Modo Usuario
            </Heading>

            <SimpleGrid columns={3} spacing={4} justifyItems="center">
              {/* Fila 1 - Columna 1: Ver equipo ganador */}
              <Link href="/equipo-ganador">
                <Button colorScheme="teal" w="100%">
                  Ver equipo ganador
                </Button>
              </Link>

              {/* Fila 1 - Columna 2: Estadísticas del equipo */}
              <Link href="/estadistica-equipo">
                <Button colorScheme="teal" w="100%">
                  Estadísticas del equipo
                </Button>
              </Link>

              {/* Resto de botones como “Funcionalidad en construcción” */}
              {Array.from({ length: 4 }).map((_, index) => (
                <Button key={index} w="100%" isDisabled variant="outline">
                  Funcionalidad en construcción
                </Button>
              ))}
            </SimpleGrid>

            <Button mt={8} onClick={() => setMode(null)}>
              Volver
            </Button>
          </Box>
        )}
      </Container>
    </ChakraProvider>
  );
}
