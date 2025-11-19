'use client';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from 'react';
import { ChakraProvider, Container, Heading, Button, Box, Alert, AlertIcon } from '@chakra-ui/react';
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
            <p className="mb-4">Selecciona un modo para continuar</p>
            <Button colorScheme="teal" onClick={() => setMode('usuario')} mr={3}>
              Modo Usuario
            </Button>
            <Link href="/pruebas" passHref>
              <Button as="a" colorScheme="blue">
                Modo pruebas
              </Button>
            </Link>
          </Box>
        )}

        {mode === 'usuario' && (
          <Box>
            <Alert status="info">
              <AlertIcon />
              En construcción
            </Alert>
            <Button mt={4} onClick={() => setMode(null)}>Volver</Button>
          </Box>
        )}
      </Container>
    </ChakraProvider>
  );
}
